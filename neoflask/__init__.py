import os
from connexion import FlaskApp
from dotenv import load_dotenv
from .cache import init_cache
from .config import Config
from flask_cors import CORS
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

init_cache(app)

from . import views
