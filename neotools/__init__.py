import os
from pathlib import Path
from dotenv import load_dotenv
from neotools.db import Instance

load_dotenv()
NEO_URI = os.getenv('NEO_URI')
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")
DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)
