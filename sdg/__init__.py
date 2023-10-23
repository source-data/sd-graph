import os
from dotenv import load_dotenv
from neotools.db import Instance

load_dotenv()
NEO_URI = os.getenv('NEO_URI')
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")
SD_API_URL = os.getenv("SD_API_URL")
SD_API_USERNAME = os.getenv("SD_API_USERNAME")
SD_API_PASSWORD = os.getenv("SD_API_PASSWORD")
DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)
EEB_INTERNAL_API = os.getenv("EEB_INTERNAL_API")
EEB_PUBLIC_API = os.getenv("EEB_PUBLIC_API")
