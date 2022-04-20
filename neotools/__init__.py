import os
from pathlib import Path
from dotenv import load_dotenv
from neotools.db import Instance

load_dotenv()
def get_db():
    NEO_URI = os.getenv('NEO_URI')
    NEO_USERNAME = os.getenv("NEO_USERNAME")
    NEO_PASSWORD = os.getenv("NEO_PASSWORD")
    return Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)
