import os
from dotenv import load_dotenv
from flask import Flask
from neotools.db import Instance
from .config import Config
from flask_cors import CORS


load_dotenv()
NEO_URI = os.getenv('NEO_URI')
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")
print(__name__)
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})


# Config.init_app(app)
# app.config.from_object(Config)

DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)

from . import views