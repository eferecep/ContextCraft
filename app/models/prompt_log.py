import json
from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

if TYPE_CHECKING:
    from app.models.project import Project


class PromptLog(db.Model):
    """optimize_prompt() sonuçlarının proje bazlı geçmişi."""

    __tablename__ = "prompt_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), index=True)
    user_prompt: Mapped[str] = mapped_column(Text)
    optimized_prompt: Mapped[str] = mapped_column(Text)
    required_files_json: Mapped[str] = mapped_column(Text, default="[]")
    explanation: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    project: Mapped["Project"] = relationship(back_populates="prompt_logs")

    @property
    def required_files(self) -> List[str]:
        try:
            data = json.loads(self.required_files_json or "[]")
        except (json.JSONDecodeError, TypeError):
            return []
        if not isinstance(data, list):
            return []
        return [item for item in data if isinstance(item, str)]

    @required_files.setter
    def required_files(self, files: List[str]) -> None:
        self.required_files_json = json.dumps(files, ensure_ascii=False)

    def __repr__(self) -> str:
        return f"<PromptLog project_id={self.project_id} id={self.id}>"
