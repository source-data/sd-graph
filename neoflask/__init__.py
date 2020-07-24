import os
from dotenv import load_dotenv
from flask import Flask
from neotools.db import Instance
from .config import Config
from flask_cors import CORS
from flask_caching import Cache


load_dotenv()
NEO_URI = os.getenv('NEO_URI')
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")

app = Flask(__name__)

CORS(app)  # , resources={r"/*": {"origins": "*"}})

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

DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)

from . import views
