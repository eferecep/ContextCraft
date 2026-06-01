from urllib.parse import urlparse

from flask import current_app, redirect, render_template, request, session, url_for

from . import main_bp


@main_bp.route("/")
def index():
    return render_template("main/index.html")


@main_bp.route("/set-language/<lang>")
def set_language(lang):
    supported = current_app.config.get("BABEL_SUPPORTED_LOCALES", ["tr", "en"])
    if lang in supported:
        session["locale"] = lang

    referrer = request.referrer
    if referrer:
        parsed = urlparse(referrer)
        if parsed.netloc in ("", request.host):
            return redirect(referrer)

    return redirect(url_for("main.index"))
