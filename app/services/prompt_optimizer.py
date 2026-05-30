import json
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

from app.models import Project
from app.services.llamaindex_service import IndexBuildError, retrieve
from app.services.openrouter import OpenRouterError, get_deepseek_client
from app.utils import list_project_files

DEEPSEEK_TEMPERATURE = 0.3
DEEPSEEK_MAX_TOKENS = 2048
MAX_REQUIRED_FILES = 3
MAX_CONTEXT_FILES = 4
MAX_CHUNKS_PER_FILE = 2

PROMPT_KEYWORDS = (
    "login", "giriş", "auth", "oauth", "token", "credential", "register",
    "kayıt", "ekran", "screen", "ui", "html", "form", "password", "şifre",
    "session", "logout", "çıkış", "user", "kullanıcı",
)

KEYWORD_RELATIONS = {
    "login": ("auth", "oauth", "credential", "token", "form"),
    "giriş": ("auth", "login", "form"),
    "ekran": ("html", "ui", "form", "screen"),
    "kayıt": ("register", "auth", "form"),
    "register": ("auth", "form", "login"),
}


def _extract_prompt_keywords(prompt: str) -> List[str]:
    lowered = (prompt or "").lower()
    keywords: List[str] = []

    for keyword in PROMPT_KEYWORDS:
        if keyword in lowered and keyword not in keywords:
            keywords.append(keyword)

    for keyword in list(keywords):
        for related in KEYWORD_RELATIONS.get(keyword, ()):
            if related not in keywords:
                keywords.append(related)

    return keywords

SYSTEM_PROMPT = """Sen ContextCraft adlı bir prompt optimizasyon asistanısın. ContextCraft bir sohbet uygulaması DEĞİLDİR.

Görevin:
1. Kullanıcının kısa isteğini, verilen proje kod parçalarına dayanarak Claude veya ChatGPT'ye yapıştırılacak detaylı bir prompt haline getirmek.
2. Bu isteği gerçekleştirmek için hangi dosyaların yeterli olduğunu seçmek.

Kurallar:
- Yalnızca verilen kod parçalarına ve kullanıcı isteğine dayan.
- Tahmin etme, uydurma dosya veya kod ekleme.
- required_files yalnızca verilen parçalarda geçen dosya yollarından seçilmeli.
- Token tasarrufu kritik: mümkün olan EN AZ dosyayı seç (çoğu istek için 1-2 dosya yeterli, en fazla 3).
- Retrieve edilen tüm dosyaları listeleme; yalnızca isteği doğrudan karşılayan dosyaları seç.
- Alakasız dosyaları (farklı modül, farklı işlev) required_files'a ekleme.
- optimized_prompt hedef AI aracına (Claude/ChatGPT) doğrudan yapıştırılacak net talimatlar içermeli.
- explanation Türkçe olmalı.
- Yanıtın YALNIZCA geçerli JSON olsun; markdown, kod bloğu veya ek metin ekleme.

JSON formatı:
{
  "optimized_prompt": "...",
  "required_files": ["path/to/file.py"],
  "explanation": "..."
}"""


class PromptOptimizeError(Exception):
    """Prompt optimizasyonu sırasında oluşan hatalar."""


def _validate_prompt(user_prompt: str) -> str:
    prompt = (user_prompt or "").strip()
    if not prompt:
        raise PromptOptimizeError("Prompt metni boş olamaz.")
    return prompt


def _validate_project_indexed(project: Project) -> None:
    if project.status != "indexed":
        raise PromptOptimizeError(
            "Proje henüz indekslenmemiş. Önce 'İndeksle' butonuna basın."
        )


def _validate_api_configured() -> None:
    openrouter_key = current_app.config.get("OPENROUTER_API_KEY", "")
    llama_key = current_app.config.get("LLAMAINDEX_API_KEY", "")
    if not openrouter_key:
        raise PromptOptimizeError(
            "OPENROUTER_API_KEY tanımlı değil. .env dosyasını kontrol edin."
        )
    if not llama_key:
        raise PromptOptimizeError(
            "LLAMAINDEX_API_KEY tanımlı değil. OpenRouter anahtarınızı "
            "LLAMAINDEX_API_KEY veya OPENROUTER_API_KEY olarak .env dosyasına ekleyin."
        )


def _keyword_relevance(chunk: Dict[str, Any], keywords: List[str]) -> float:
    if not keywords:
        return 0.0

    path = (chunk.get("file_path") or "").lower()
    symbol = (chunk.get("symbol_name") or "").lower()
    text = (chunk.get("text") or "")[:800].lower()
    boost = 0.0

    for keyword in keywords:
        if keyword in path:
            boost += 0.08
        if keyword in symbol:
            boost += 0.04
        if keyword in text:
            boost += 0.015

    return boost


def _score_files(chunks: List[Dict[str, Any]], prompt: str = "") -> Dict[str, float]:
    keywords = _extract_prompt_keywords(prompt)
    scores: Dict[str, float] = {}

    for chunk in chunks:
        path = _normalize_file_path(chunk.get("file_path") or "")
        if not path:
            continue
        score = float(chunk.get("score") or 0.0) + _keyword_relevance(chunk, keywords)
        scores[path] = max(scores.get(path, 0.0), score)

    return scores


def _rank_files(chunks: List[Dict[str, Any]], prompt: str = "") -> List[str]:
    scores = _score_files(chunks, prompt)
    return sorted(scores.keys(), key=lambda path: scores[path], reverse=True)


def _prioritize_chunks(
    chunks: List[Dict[str, Any]],
    prompt: str,
    max_files: int = MAX_CONTEXT_FILES,
    max_chunks_per_file: int = MAX_CHUNKS_PER_FILE,
) -> List[Dict[str, Any]]:
    """Retrieve sonuçlarını prompt ile yeniden sıralayıp dosya başına sınırlar."""
    if not chunks:
        return []

    ranked_files = _rank_files(chunks, prompt)[:max_files]
    allowed_files = set(ranked_files)

    grouped: Dict[str, List[Dict[str, Any]]] = {path: [] for path in ranked_files}
    for chunk in chunks:
        path = _normalize_file_path(chunk.get("file_path") or "")
        if path in allowed_files:
            grouped[path].append(chunk)

    prioritized: List[Dict[str, Any]] = []
    for path in ranked_files:
        file_chunks = grouped.get(path, [])
        child_chunks = [chunk for chunk in file_chunks if chunk.get("chunk_type") == "child"]
        candidates = child_chunks or file_chunks
        candidates.sort(
            key=lambda chunk: float(chunk.get("score") or 0.0)
            + _keyword_relevance(chunk, _extract_prompt_keywords(prompt)),
            reverse=True,
        )
        for chunk in candidates[:max_chunks_per_file]:
            chunk_copy = dict(chunk)
            chunk_copy["score"] = float(chunk.get("score") or 0.0) + _keyword_relevance(
                chunk, _extract_prompt_keywords(prompt)
            )
            prioritized.append(chunk_copy)

    prioritized.sort(key=lambda chunk: float(chunk.get("score") or 0.0), reverse=True)
    return prioritized


def _format_file_ranking(chunks: List[Dict[str, Any]], prompt: str) -> str:
    ranked_files = _rank_files(chunks, prompt)
    if not ranked_files:
        return "Aday dosya bulunamadı."

    lines: List[str] = []
    for index, path in enumerate(ranked_files, start=1):
        lines.append(f"{index}. {path}")
    return "\n".join(lines)


def _refine_required_files(
    required_files: List[str],
    chunks: List[Dict[str, Any]],
    prompt: str,
    max_files: int = MAX_REQUIRED_FILES,
) -> List[str]:
    """LLM çıktısını retrieve skorlarıyla sınırlar; boşsa en alakalı dosyaları seçer."""
    ranked_files = _rank_files(chunks, prompt)
    if not ranked_files:
        return []

    if not required_files:
        return ranked_files[:min(2, max_files)]

    if len(required_files) <= max_files:
        return required_files

    required_set = set(required_files)
    filtered = [path for path in ranked_files if path in required_set]
    return filtered[:max_files]


def _format_chunk_header(chunk: Dict[str, Any]) -> str:
    file_path = chunk.get("file_path") or "bilinmeyen"
    symbol_name = chunk.get("symbol_name") or "-"
    start_line = chunk.get("start_line")
    end_line = chunk.get("end_line")

    if start_line is not None and end_line is not None:
        line_info = f"satır {start_line}-{end_line}"
    elif start_line is not None:
        line_info = f"satır {start_line}"
    else:
        line_info = "satır ?"

    return f"[{file_path} | {symbol_name} | {line_info}]"


def format_retrieved_chunks(chunks: List[Dict[str, Any]]) -> str:
    """Retrieve edilen parçaları DeepSeek'e gönderilecek metne çevirir."""
    sections: List[str] = []

    for chunk in chunks:
        header = _format_chunk_header(chunk)
        text = (chunk.get("text") or "").strip()
        sections.append(f"{header}\n{text}")

    return "\n\n".join(sections)


def _retrieve_context(project: Project, prompt: str) -> Tuple[List[Dict[str, Any]], str]:
    try:
        raw_chunks = retrieve(project, prompt)
    except IndexBuildError as exc:
        raise PromptOptimizeError(str(exc)) from exc

    if not raw_chunks:
        raise PromptOptimizeError(
            "İlgili kod parçası bulunamadı. Promptu farklı kelimelerle deneyin."
        )

    chunks = _prioritize_chunks(raw_chunks, prompt)
    return chunks, format_retrieved_chunks(chunks)


def _build_user_message(
    user_prompt: str,
    context_text: str,
    chunks: List[Dict[str, Any]],
) -> str:
    file_ranking = _format_file_ranking(chunks, user_prompt)
    return (
        "Kullanıcı isteği:\n"
        f"{user_prompt}\n\n"
        "Aday dosyalar (alakaya göre sıralı — yalnızca gerekli olanları seç):\n"
        f"{file_ranking}\n\n"
        "Proje kod parçaları (retrieve edildi):\n"
        f"{context_text}"
    )


def _call_deepseek(
    user_prompt: str,
    context_text: str,
    chunks: List[Dict[str, Any]],
) -> str:
    """DeepSeek V3.1'e system + user mesajı gönderir, ham yanıt döndürür."""
    client = get_deepseek_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": _build_user_message(user_prompt, context_text, chunks),
        },
    ]

    try:
        return client.chat(
            messages,
            temperature=DEEPSEEK_TEMPERATURE,
            max_tokens=DEEPSEEK_MAX_TOKENS,
        )
    except OpenRouterError as exc:
        raise PromptOptimizeError(str(exc)) from exc


def _extract_json_text(raw_response: str) -> str:
    text = raw_response.strip()
    if not text.startswith("```"):
        return text

    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _known_file_paths(chunks: List[Dict[str, Any]]) -> List[str]:
    paths: List[str] = []
    seen = set()

    for chunk in chunks:
        path = _normalize_file_path(chunk.get("file_path") or "")
        if path and path not in seen:
            seen.add(path)
            paths.append(path)

    return paths


def _normalize_file_path(path: str) -> str:
    normalized = path.strip().replace("\\", "/")
    if normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized


def _match_known_path(candidate: str, known_paths: List[str]) -> Optional[str]:
    candidate = _normalize_file_path(candidate)
    if not candidate:
        return None

    if candidate in known_paths:
        return candidate

    for known in known_paths:
        if known.endswith("/" + candidate):
            return known

    candidate_base = candidate.split("/")[-1]
    basename_matches = [
        known for known in known_paths if known.split("/")[-1] == candidate_base
    ]
    if len(basename_matches) == 1:
        return basename_matches[0]

    return None


def _normalize_required_files(
    files: Any,
    known_paths: List[str],
) -> List[str]:
    if not isinstance(files, list):
        return []

    result: List[str] = []
    seen = set()

    for item in files:
        if not isinstance(item, str):
            continue

        matched = _match_known_path(item, known_paths)
        if matched and matched not in seen:
            seen.add(matched)
            result.append(matched)

    return result


def _parse_deepseek_response(
    raw_response: str,
    chunks: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """DeepSeek yanıtını JSON'a çevirir; başarısız olursa ham metne düşer."""
    known_paths = _known_file_paths(chunks)
    fallback: Dict[str, Any] = {
        "optimized_prompt": raw_response.strip(),
        "required_files": [],
        "explanation": "",
    }

    try:
        data = json.loads(_extract_json_text(raw_response))
    except (json.JSONDecodeError, TypeError):
        return fallback

    if not isinstance(data, dict):
        return fallback

    optimized_prompt = data.get("optimized_prompt", "")
    if not isinstance(optimized_prompt, str):
        optimized_prompt = str(optimized_prompt) if optimized_prompt is not None else ""

    explanation = data.get("explanation", "")
    if not isinstance(explanation, str):
        explanation = str(explanation) if explanation is not None else ""

    if not optimized_prompt.strip():
        return fallback

    return {
        "optimized_prompt": optimized_prompt.strip(),
        "required_files": _normalize_required_files(
            data.get("required_files"),
            known_paths,
        ),
        "explanation": explanation.strip(),
    }


def optimize_prompt(project: Project, user_prompt: str) -> Dict[str, Any]:
    """
    Kullanıcı promptunu proje bağlamına göre optimize eder.

    Adım 6.1: ön kontroller.
    Adım 6.2: retrieve → bağlam metni.
    Adım 6.3: DeepSeek API çağrısı.
    Adım 6.4: yanıt parse → { optimized_prompt, required_files, explanation, ... }
    """
    prompt = _validate_prompt(user_prompt)
    _validate_project_indexed(project)
    _validate_api_configured()

    chunks, context_text = _retrieve_context(project, prompt)
    raw_response = _call_deepseek(prompt, context_text, chunks)
    result = _parse_deepseek_response(raw_response, chunks)
    result["required_files"] = _refine_required_files(
        result.get("required_files") or [],
        chunks,
        prompt,
    )
    result["retrieved_count"] = len(chunks)
    result["total_files"] = len(list_project_files(project.source_path or ""))
    return result
