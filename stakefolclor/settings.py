import os
import dj_database_url
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-local-dev-only")
DEBUG = os.environ.get("DEBUG", "True") == "True"
ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "cloudinary_storage",  
    "django.contrib.staticfiles",
    "cloudinary",
    "crispy_forms",
    "crispy_bootstrap5",
    "core",
    "accounts",
    "contests",
    "predictions",
    "dashboard",
    "bets",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "stakefolclor.urls"

TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"],
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.debug",
        "django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
        "core.context_processors.global_context",
    ]},
}]

WSGI_APPLICATION = "stakefolclor.wsgi.application"

DATABASE_URL = os.environ.get("DATABASE_URL")
if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            ssl_require=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "stakefolclor"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "localhost"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }

AUTH_USER_MODEL = "accounts.CustomUser"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 8}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es-pe"
TIME_ZONE     = "America/Lima"
USE_I18N = True
USE_TZ   = True

STATIC_URL   = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT  = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

MEDIA_URL  = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Cloudinary - almacenamiento de imagenes en produccion
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.environ.get("CLOUDINARY_CLOUD_NAME"),
    "API_KEY":    os.environ.get("CLOUDINARY_API_KEY"),
    "API_SECRET": os.environ.get("CLOUDINARY_API_SECRET"),
}

if os.environ.get("CLOUDINARY_CLOUD_NAME"):
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL           = "/accounts/login/"
LOGIN_REDIRECT_URL  = "/"
LOGOUT_REDIRECT_URL = "/"

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

UNFOLD = {
    "SITE_TITLE":  "StakeFolclor",
    "SITE_HEADER": "Control Center",
    "SITE_URL":    "/",
    "SITE_SYMBOL": "theater_comedy",
    "SHOW_HISTORY": True,
    "COLORS": {"primary": {
        "50":"250 245 255","100":"243 232 255","200":"233 213 255",
        "300":"216 180 254","400":"192 132 252","500":"168 85 247",
        "600":"147 51 234","700":"126 34 206","800":"107 33 168",
        "900":"88 28 135","950":"59 7 100",
    }},
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {"title":"Panel","separator":True,"items":[
                {"title":"Dashboard","icon":"dashboard","link":"/system-control-panel-89721/"},
            ]},
            {"title":"Concursos","separator":True,"items":[
                {"title":"Concursos",   "icon":"emoji_events", "link":"/system-control-panel-89721/contests/contest/"},
                {"title":"Bloques",     "icon":"grid_view",    "link":"/system-control-panel-89721/contests/block/"},
                {"title":"Agrupaciones","icon":"groups",       "link":"/system-control-panel-89721/contests/group/"},
                {"title":"Jurados",     "icon":"gavel",        "link":"/system-control-panel-89721/contests/judge/"},
                {"title":"Puntajes",    "icon":"scoreboard",   "link":"/system-control-panel-89721/contests/score/"},
            ]},
            {"title":"Final","separator":True,"items":[
                {"title":"Tabla Final","icon":"military_tech",     "link":"/system-control-panel-89721/contests/finalgroup/"},
                {"title":"Podio",      "icon":"workspace_premium", "link":"/system-control-panel-89721/contests/finalresult/"},
            ]},
            {"title":"Apuestas","separator":True,"items":[
                {"title":"Opciones",   "icon":"bolt",                "link":"/system-control-panel-89721/bets/betoption/"},
                {"title":"Tickets",    "icon":"confirmation_number", "link":"/system-control-panel-89721/bets/bet/"},
                {"title":"Billeteras", "icon":"wallet",              "link":"/system-control-panel-89721/bets/wallet/"},
            ]},
            {"title":"Predicciones","separator":True,"items":[
                {"title":"Predicciones","icon":"psychology","link":"/system-control-panel-89721/predictions/prediction/"},
            ]},
            {"title":"Usuarios","separator":True,"items":[
                {"title":"Usuarios","icon":"manage_accounts","link":"/system-control-panel-89721/accounts/customuser/"},
            ]},
        ],
    },
}

