"""Flask-Babel locale seçimi."""

from flask import current_app, has_request_context, request, session


def get_locale() -> str:
    """Oturum, Accept-Language veya varsayılan (tr) locale döndürür."""
    if not has_request_context():
        return "tr"

    supported = current_app.config.get("BABEL_SUPPORTED_LOCALES", ["tr", "en"])
    locale = session.get("locale")
    if locale in supported:
        return locale

    best_match = request.accept_languages.best_match(supported)
    if best_match:
        return best_match

    return current_app.config.get("BABEL_DEFAULT_LOCALE", "tr")
