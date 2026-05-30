from typing import Any, Dict, List

from flask import current_app

from app.models import Project


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


def optimize_prompt(project: Project, user_prompt: str) -> Dict[str, Any]:
    """
    Kullanıcı promptunu proje bağlamına göre optimize eder.

    Adım 6.1: ön kontroller.
    Adım 6.2+: retrieve → DeepSeek → { optimized_prompt, required_files, explanation }
    """
    _validate_prompt(user_prompt)
    _validate_project_indexed(project)
    _validate_api_configured()

    # Adım 6.2'de retrieve + DeepSeek entegrasyonu eklenecek.
    result: Dict[str, Any] = {
        "optimized_prompt": "",
        "required_files": [],
        "explanation": "",
    }
    return result
