from flask import Flask


def create_app() -> Flask:
    app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")
    from .routes import main
    app.register_blueprint(main)
    return app
