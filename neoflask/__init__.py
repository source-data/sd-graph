import os
from connexion import FlaskApp
from dotenv import load_dotenv
from neotools.db import Instance
from .config import Config
from flask_cors import CORS
from flask_caching import Cache
from swagger_server import encoder


load_dotenv()
EEB_INTERNAL_API = os.getenv("EEB_INTERNAL_API")

connexion_app = FlaskApp(__name__, specification_dir='../api/server/swagger_server/swagger/')
app = connexion_app.app

connexion_app.add_api(
    'swagger.yaml',
    arguments={'title': 'Early Evidence Base API'},
    pythonic_params=True,
    strict_validation=True,
)
app.json_encoder = encoder.JSONEncoder

CORS(app, resources={r"/api/*": {"origins": "*"}})

Config.init_app(app)
app.config.from_object(Config)

cache = Cache(config={
    'CACHE_DEFAULT_TIMEOUT': 365 * 24 * 60 * 60,
    'CACHE_KEY_PREFIX': __name__,
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': '6379',
    # 'CACHE_THRESHOLD': 1000,
    # 'CACHE_REDIS_PASSWORD': '',
    # 'CACHE_REDIS_DB': '',
    # 'CACHE_ARGS': '',
    # 'CACHE_OPTIONS': '',
    # 'CACHE_REDIS_URL': '',
})

cache.init_app(app)
with app.app_context():
    cache.clear()

from . import views
