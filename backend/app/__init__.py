from flask import Flask
from .routes import main

def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../frontend/static",
    )

    app.config.from_object("app.config.Config")
    app.register_blueprint(main)

    return app
