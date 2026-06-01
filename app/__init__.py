from flask import Flask, render_template

from config import config

from .extensions import babel, csrf, db, login_manager, migrate
from .i18n import get_locale


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def create_app(config_name="default"):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    @app.context_processor
    def inject_i18n():
        return {
            "LANGUAGES": app.config.get("LANGUAGES", {}),
            "current_locale": get_locale(),
        }

    from . import models  # noqa: F401
    from .models import User

    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from .auth import auth_bp
    from .core import core_bp
    from .main import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)

    _register_error_handlers(app)

    return app
