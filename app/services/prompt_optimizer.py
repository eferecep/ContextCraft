import json
from typing import Any, Dict, List, Optional, Tuple

from flask import current_app

from app.models import Project
from app.services.llamaindex_service import IndexBuildError, retrieve
from app.services.openrouter import OpenRouterError, get_deepseek_client
from app.utils import list_project_files

DEEPSEEK_TEMPERATURE = 0.3
DEEPSEEK_MAX_TOKENS = 2048

SYSTEM_PROMPT = """Sen ContextCraft adlı bir prompt optimizasyon asistanısın. ContextCraft bir sohbet uygulaması DEĞİLDİR.

Görevin:
1. Kullanıcının kısa isteğini, verilen proje kod parçalarına dayanarak Claude veya ChatGPT'ye yapıştırılacak detaylı bir prompt haline getirmek.
2. Bu isteği gerçekleştirmek için hangi dosyaların yeterli olduğunu seçmek.

Kurallar:
- Yalnızca verilen kod parçalarına ve kullanıcı isteğine dayan.
- Tahmin etme, uydurma dosya veya kod ekleme.
- required_files yalnızca verilen parçalarda geçen dosya yollarından seçilmeli.
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
    api_key = current_app.config.get("OPENROUTER_API_KEY", "")
    if not api_key:
        raise PromptOptimizeError(
            "OPENROUTER_API_KEY tanımlı değil. .env dosyasını kontrol edin."
        )


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
        chunks = retrieve(project, prompt)
    except IndexBuildError as exc:
        raise PromptOptimizeError(str(exc)) from exc

    if not chunks:
        raise PromptOptimizeError(
            "İlgili kod parçası bulunamadı. Promptu farklı kelimelerle deneyin."
        )

    return chunks, format_retrieved_chunks(chunks)


def _build_user_message(user_prompt: str, context_text: str) -> str:
    return (
        "Kullanıcı isteği:\n"
        f"{user_prompt}\n\n"
        "Proje kod parçaları (retrieve edildi):\n"
        f"{context_text}"
    )


def _call_deepseek(user_prompt: str, context_text: str) -> str:
    """DeepSeek V3.1'e system + user mesajı gönderir, ham yanıt döndürür."""
    client = get_deepseek_client()
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": _build_user_message(user_prompt, context_text)},
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
        if known.split("/")[-1] == candidate.split("/")[-1]:
            return known

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
    raw_response = _call_deepseek(prompt, context_text)
    result = _parse_deepseek_response(raw_response, chunks)
    result["retrieved_count"] = len(chunks)
    result["total_files"] = len(list_project_files(project.source_path or ""))
    return result
