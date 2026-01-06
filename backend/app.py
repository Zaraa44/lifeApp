from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

# ===== PAGES / ROUTES =====


# ===== API BLUEPRINTS =====
from api.google_fit import google_fit
from api.weight import weight_api
from api.profile import profile_api
from api.kcal import kcal_api
from api.routes import main


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
