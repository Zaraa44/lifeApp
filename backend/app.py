from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from backend.api.google_fit import google_fit
from backend.api.kcal import kcal_api
from backend.api.profile import profile_api
from backend.api.routes import main
from backend.api.weight import weight_api

# ===== PAGES / ROUTES =====


# ===== API BLUEPRINTS =====


app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static",
)

# ===== CONFIG =====
app.config["SECRET_KEY"] = "dev-secret-key"  # vervang in prod via env
app.config["GOOGLE_CLIENT_ID"] = ""
app.config["GOOGLE_CLIENT_SECRET"] = ""
app.config["GOOGLE_REDIRECT_URI"] = ""

# ===== PROXY FIX (Vercel / HTTPS) =====
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ===== REGISTER ROUTES =====
app.register_blueprint(main)
app.register_blueprint(google_fit)
app.register_blueprint(weight_api)
app.register_blueprint(profile_api)
app.register_blueprint(kcal_api)


if __name__ == "__main__":
    app.run(debug=True)
