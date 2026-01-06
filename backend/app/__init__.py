from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .kcal import kcal_api
from .profile import profile_api
from .routes import main
from .google_fit import google_fit
from .weight import weight_api


def create_app():
    app = Flask(
        __name__,
        template_folder="../../frontend/templates",
        static_folder="../../frontend/static",
    )

    app.config.from_object("app.config.Config")
    app.register_blueprint(main)
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_proto=1,
        x_host=1
    )
    app.register_blueprint(google_fit)
    app.register_blueprint(weight_api)
    app.register_blueprint(profile_api)
    app.register_blueprint(kcal_api)
    return app
