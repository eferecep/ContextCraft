import ast
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app
from llama_index.core import StorageContext, VectorStoreIndex, load_index_from_storage
from llama_index.core.llms.mock import MockLLM
from llama_index.core.retrievers import QueryFusionRetriever
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.retrievers.bm25 import BM25Retriever

from app.models import Project
from app.utils.index_helpers import (
    collect_indexable_files,
    delete_storage_dir,
    ensure_storage_parent,
    extract_zip_archives,
    get_storage_dir,
    read_project_file,
)

RETRIEVE_TOP_K = 10
CHILD_CHUNK_LINES = 80
MAX_PARENT_CHARS = 12000


class IndexBuildError(Exception):
    """LlamaIndex indeksleme sırasında oluşan hatalar."""


def _normalize_embedding_model(model: str) -> str:
    """
    LlamaIndex OpenAIEmbedding yalnızca OpenAI model slug'larını tanır.
    OpenRouter .env değeri openai/text-embedding-3-small ise text-embedding-3-small'a çevirir.
    """
    if model.startswith("openai/"):
        return model.split("/", 1)[1]
    return model


def _get_embed_model() -> OpenAIEmbedding:
    """OpenRouter üzerinden embedding — yerel model indirilmez."""
    api_key = current_app.config.get("LLAMAINDEX_API_KEY", "")
    if not api_key:
        raise IndexBuildError(
            "LLAMAINDEX_API_KEY tanımlı değil. .env dosyasını kontrol edin."
        )

    raw_model = current_app.config.get(
        "LLAMAINDEX_EMBEDDING_MODEL", "text-embedding-3-small"
    )
    model = _normalize_embedding_model(raw_model)

    return OpenAIEmbedding(
        model=model,
        api_key=api_key,
        api_base=current_app.config.get(
            "LLAMAINDEX_API_BASE", "https://openrouter.ai/api/v1"
        ),
        default_headers={
            "HTTP-Referer": current_app.config.get(
                "OPENROUTER_SITE_URL", "http://localhost:5000"
            ),
            "X-Title": current_app.config.get("OPENROUTER_APP_NAME", "ContextCraft"),
        },
    )


def _file_type(relative_path: Path) -> str:
    suffix = relative_path.suffix.lower().lstrip(".")
    return suffix or "text"


def _line_chunks(
    content: str, lines_per_chunk: int = CHILD_CHUNK_LINES
) -> List[Tuple[str, int, int]]:
    lines = content.splitlines()
    if not lines:
        return []

    chunks: List[Tuple[str, int, int]] = []
    for start_idx in range(0, len(lines), lines_per_chunk):
        end_idx = min(start_idx + lines_per_chunk, len(lines))
        chunk_text = "\n".join(lines[start_idx:end_idx])
        chunks.append((chunk_text, start_idx + 1, end_idx))
    return chunks


def _python_symbols(content: str) -> List[Tuple[str, str, int, int]]:
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    lines = content.splitlines()
    symbols: List[Tuple[str, str, int, int]] = []
    for node in ast.walk(tree):
        if not isinstance(
            node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
        ):
            continue

        start_line = node.lineno
        end_line = getattr(node, "end_lineno", None) or start_line
        start_idx = max(start_line - 1, 0)
        end_idx = min(end_line, len(lines))
        chunk_text = "\n".join(lines[start_idx:end_idx])
        symbols.append((node.name, chunk_text, start_line, end_line))

    return symbols


def _build_file_nodes(
    relative_path: Path, content: str
) -> List[TextNode]:
    """Parent (dosya bağlamı) + child (fonksiyon/blok) node'ları üretir."""
    file_path = str(relative_path).replace("\\", "/")
    file_type = _file_type(relative_path)
    nodes: List[TextNode] = []

    parent_text = content
    if len(parent_text) > MAX_PARENT_CHARS:
        parent_text = parent_text[:MAX_PARENT_CHARS] + "\n... (kısaltıldı)"

    parent_id = f"{file_path}::parent"
    nodes.append(
        TextNode(
            text=parent_text,
            id_=parent_id,
            metadata={
                "file_path": file_path,
                "symbol_name": "",
                "start_line": 1,
                "end_line": len(content.splitlines()) or 1,
                "file_type": file_type,
                "chunk_type": "parent",
            },
        )
    )

    if file_type == "py":
        symbols = _python_symbols(content)
        if symbols:
            for index, (symbol_name, symbol_text, start_line, end_line) in enumerate(
                symbols
            ):
                nodes.append(
                    TextNode(
                        text=symbol_text,
                        id_=f"{file_path}::child::{index}",
                        metadata={
                            "file_path": file_path,
                            "symbol_name": symbol_name,
                            "start_line": start_line,
                            "end_line": end_line,
                            "file_type": file_type,
                            "chunk_type": "child",
                        },
                    )
                )
            return nodes

    for index, (chunk_text, start_line, end_line) in enumerate(
        _line_chunks(content)
    ):
        nodes.append(
            TextNode(
                text=chunk_text,
                id_=f"{file_path}::child::{index}",
                metadata={
                    "file_path": file_path,
                    "symbol_name": f"block_{index + 1}",
                    "start_line": start_line,
                    "end_line": end_line,
                    "file_type": file_type,
                    "chunk_type": "child",
                },
            )
        )

    return nodes


def _build_all_nodes(source_path: str) -> List[TextNode]:
    root = Path(source_path)
    relative_files = collect_indexable_files(source_path)
    if not relative_files:
        raise IndexBuildError("İndekslenecek metin dosyası bulunamadı.")

    all_nodes: List[TextNode] = []
    for relative_path in relative_files:
        content = read_project_file(root, relative_path)
        if not content.strip():
            continue
        all_nodes.extend(_build_file_nodes(relative_path, content))

    if not all_nodes:
        raise IndexBuildError("Dosyalardan geçerli içerik parçası üretilemedi.")

    return all_nodes


def _get_hybrid_retriever(
    index: VectorStoreIndex, top_k: int = RETRIEVE_TOP_K
) -> QueryFusionRetriever:
    vector_retriever = index.as_retriever(similarity_top_k=top_k)
    bm25_retriever = BM25Retriever.from_defaults(
        docstore=index.docstore,
        similarity_top_k=top_k,
    )
    return QueryFusionRetriever(
        [vector_retriever, bm25_retriever],
        llm=MockLLM(),
        similarity_top_k=top_k,
        num_queries=1,
        mode="reciprocal_rerank",
        use_async=False,
    )


def build_project_index(project: Project) -> int:
    """
    Projeyi indeksler ve storage/ altına persist eder.
    Dönen değer: oluşturulan node sayısı.
    """
    if not project.source_path:
        raise IndexBuildError("Proje dosya yolu tanımlı değil.")

    source_root = Path(project.source_path)
    if not source_root.is_dir():
        raise IndexBuildError("Proje klasörü bulunamadı.")

    delete_storage_dir(project.owner_id, project.id)
    extract_zip_archives(source_root)

    nodes = _build_all_nodes(str(source_root))
    embed_model = _get_embed_model()

    index = VectorStoreIndex(nodes, embed_model=embed_model)
    storage_dir = ensure_storage_parent(
        get_storage_dir(project.owner_id, project.id)
    )
    index.storage_context.persist(persist_dir=str(storage_dir))

    meta = {
        "node_count": len(nodes),
        "file_count": len(collect_indexable_files(str(source_root))),
    }
    (storage_dir / "contextcraft_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return len(nodes)


def _load_project_index(project: Project) -> VectorStoreIndex:
    storage_dir = get_storage_dir(project.owner_id, project.id)
    if not storage_dir.exists():
        raise IndexBuildError("Proje henüz indekslenmemiş.")

    embed_model = _get_embed_model()
    storage_context = StorageContext.from_defaults(persist_dir=str(storage_dir))
    return load_index_from_storage(storage_context, embed_model=embed_model)


def retrieve(project: Project, prompt: str, top_k: int = RETRIEVE_TOP_K) -> List[Dict[str, Any]]:
    """
    Hibrit retrieve — vektör + BM25, top_k aday döndürür.
    Faz 6'da DeepSeek'e gidecek aday parçalar.
    """
    if not prompt.strip():
        raise IndexBuildError("Sorgu metni boş olamaz.")

    index = _load_project_index(project)
    retriever = _get_hybrid_retriever(index, top_k=top_k)

    results: List[NodeWithScore] = retriever.retrieve(prompt)
    output: List[Dict[str, Any]] = []

    for item in results[:top_k]:
        metadata = dict(item.node.metadata or {})
        output.append(
            {
                "score": float(item.score or 0.0),
                "text": item.node.get_content(),
                "file_path": metadata.get("file_path", ""),
                "symbol_name": metadata.get("symbol_name", ""),
                "start_line": metadata.get("start_line"),
                "end_line": metadata.get("end_line"),
                "file_type": metadata.get("file_type", ""),
                "chunk_type": metadata.get("chunk_type", ""),
            }
        )

    return output
