from flask import Blueprint

core_bp = Blueprint("core", __name__, url_prefix="/core")

from app.core import routes  # noqa: E402, F401
