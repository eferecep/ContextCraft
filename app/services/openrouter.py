import json
import os
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from flask import current_app


class OpenRouterError(Exception):
    """OpenRouter API isteği başarısız olduğunda fırlatılır."""


class DeepSeekClient:
    """OpenRouter üzerinden DeepSeek modeline istek gönderen istemci."""

    BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        site_url: Optional[str] = None,
        app_name: Optional[str] = None,
    ):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY", "")
        self.model = model or os.environ.get(
            "OPENROUTER_MODEL", "deepseek/deepseek-chat"
        )
        self.site_url = site_url or os.environ.get(
            "OPENROUTER_SITE_URL", "http://localhost:5000"
        )
        self.app_name = app_name or os.environ.get(
            "OPENROUTER_APP_NAME", "ContextCraft"
        )

    def is_configured(self) -> bool:
        return bool(self.api_key)

    def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        if not self.is_configured():
            raise OpenRouterError(
                "OPENROUTER_API_KEY tanımlı değil. .env dosyasını kontrol edin."
            )

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.site_url,
            "X-Title": self.app_name,
        }

        request = Request(
            self.BASE_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urlopen(request, timeout=60) as response:
                data = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise OpenRouterError(
                f"OpenRouter HTTP {exc.code}: {error_body}"
            ) from exc
        except URLError as exc:
            raise OpenRouterError(f"OpenRouter bağlantı hatası: {exc.reason}") from exc

        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise OpenRouterError(f"Beklenmeyen API yanıtı: {data}") from exc

    def ask(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> str:
        messages: List[Dict[str, str]] = []

        if system_message:
            messages.append({"role": "system", "content": system_message})

        messages.append({"role": "user", "content": prompt})
        return self.chat(messages, temperature=temperature, max_tokens=max_tokens)


def get_deepseek_client() -> DeepSeekClient:
    """Flask app config veya ortam değişkenlerinden DeepSeek istemcisi döndürür."""
    try:
        config = current_app.config
        return DeepSeekClient(
            api_key=config.get("OPENROUTER_API_KEY"),
            model=config.get("OPENROUTER_MODEL"),
            site_url=config.get("OPENROUTER_SITE_URL"),
            app_name=config.get("OPENROUTER_APP_NAME"),
        )
    except RuntimeError:
        return DeepSeekClient()
