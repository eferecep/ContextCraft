"""Prompt optimizasyon motoru testleri (OpenRouter mock)."""

import json
from unittest.mock import patch

import pytest

from app.extensions import db
from app.models import Project
from app.services.prompt_optimizer import (
    PromptOptimizeError,
    _extract_prompt_keywords,
    _parse_deepseek_response,
    _refine_required_files,
    optimize_prompt,
)


def test_extract_prompt_keywords_login():
    """Login isteği auth ile ilişkili anahtar kelimeleri genişletmeli."""
    keywords = _extract_prompt_keywords("login ekranı yap")
    assert "login" in keywords
    assert "ekran" in keywords
    assert "auth" in keywords


def test_parse_deepseek_response_json():
    """Geçerli JSON yanıtı doğru parse edilmeli."""
    chunks = [{"file_path": "app/auth.py", "score": 0.5}]
    raw = json.dumps(
        {
            "optimized_prompt": "Detaylı talimat",
            "required_files": ["app/auth.py"],
            "explanation": "Açıklama",
        },
        ensure_ascii=False,
    )
    result = _parse_deepseek_response(raw, chunks)
    assert result["optimized_prompt"] == "Detaylı talimat"
    assert result["required_files"] == ["app/auth.py"]
    assert result["explanation"] == "Açıklama"


def test_parse_deepseek_response_code_fence():
    """Markdown code fence içindeki JSON parse edilmeli."""
    chunks = [{"file_path": "main.py", "score": 0.4}]
    raw = '```json\n{"optimized_prompt": "OK", "required_files": ["main.py"], "explanation": ""}\n```'
    result = _parse_deepseek_response(raw, chunks)
    assert result["optimized_prompt"] == "OK"
    assert result["required_files"] == ["main.py"]


def test_refine_required_files_caps_excess():
    """Fazla dosya önerisi retrieve skoruna göre sınırlanmalı."""
    chunks = [
        {"file_path": "a.py", "score": 0.9},
        {"file_path": "b.py", "score": 0.8},
        {"file_path": "c.py", "score": 0.7},
        {"file_path": "d.py", "score": 0.6},
    ]
    refined = _refine_required_files(
        ["a.py", "b.py", "c.py", "d.py"],
        chunks,
        "login yap",
        max_files=2,
    )
    assert refined == ["a.py", "b.py"]


def test_refine_required_files_fallback_when_empty():
    """Boş LLM listesinde en alakalı dosyalar seçilmeli."""
    chunks = [
        {"file_path": "auth.py", "score": 0.9},
        {"file_path": "other.py", "score": 0.1},
    ]
    refined = _refine_required_files([], chunks, "login ekranı")
    assert refined[0] == "auth.py"
    assert len(refined) <= 2


def test_optimize_prompt_requires_indexed(app, user):
    """İndekslenmemiş proje için hata fırlatılmalı."""
    with app.app_context():
        project = Project(name="Pending", owner_id=user, status="pending")
        db.session.add(project)
        db.session.commit()

        with pytest.raises(PromptOptimizeError, match="indekslenmemiş"):
            optimize_prompt(project, "login ekranı yap")


@patch("app.services.prompt_optimizer._call_deepseek")
@patch("app.services.prompt_optimizer.retrieve")
def test_optimize_prompt_success(mock_retrieve, mock_deepseek, app, user, tmp_path):
    """Mock retrieve + DeepSeek ile optimize_prompt tam akışı."""
    project_dir = tmp_path / "proj"
    project_dir.mkdir()
    (project_dir / "auth.py").write_text("def login(): pass", encoding="utf-8")

    mock_retrieve.return_value = [
        {
            "score": 0.9,
            "text": "def login(): pass",
            "file_path": "auth.py",
            "symbol_name": "login",
            "chunk_type": "child",
        }
    ]
    mock_deepseek.return_value = json.dumps(
        {
            "optimized_prompt": "Login fonksiyonu yaz",
            "required_files": ["auth.py"],
            "explanation": "Tek dosya yeterli",
        },
        ensure_ascii=False,
    )

    with app.app_context():
        project = Project(
            name="Indexed",
            owner_id=user,
            status="indexed",
            source_path=str(project_dir),
        )
        db.session.add(project)
        db.session.commit()

        result = optimize_prompt(project, "login ekranı yap")

    assert result["optimized_prompt"] == "Login fonksiyonu yaz"
    assert result["required_files"] == ["auth.py"]
    assert result["retrieved_count"] == 1
    mock_retrieve.assert_called_once()
    mock_deepseek.assert_called_once()
