from flask import Flask

UPLOAD_FOLDER = 'uploads'  

def create_app() -> Flask:
    app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend/templates")
    from .routes import main
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.register_blueprint(main)
    return app
