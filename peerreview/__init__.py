import os
from hypothepy.v1.api import HypoApi
from dotenv import load_dotenv
from neotools.db import Instance

load_dotenv()

HYPOTHESIS_USER = os.getenv("HYPOTHESIS_USER")
HYPOTHESIS_API_KEY = os.getenv("HYPOTHESIS_API_KEY")
HYPO = HypoApi(HYPOTHESIS_API_KEY, HYPOTHESIS_USER)

NEO_URI = os.getenv('NEO_URI')
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")
DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)
