import os
import logging
from pathlib import Path
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
EEB_PUBLIC_API = os.getenv("EEB_PUBLIC_API")

# create logger
logger = logging.getLogger('sdg logger')
logger.setLevel(logging.DEBUG)
log_dir = Path('sdg/log')
log_file = Path('sdg.log')
if not log_dir.exists():
    Path.mkdir(log_dir)
log_path = log_dir / log_file
ch = logging.FileHandler(log_path, mode='w')
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)