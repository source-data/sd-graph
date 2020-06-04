import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from neotools.db import Instance

# create logger
logger = logging.getLogger('neojats logger')
logger.setLevel(logging.DEBUG)
log_dir = Path('neotools/log')
log_file = Path('neotools.log')
if not log_dir.exists():
    Path.mkdir(log_dir)
log_path = log_dir / log_file
ch = logging.FileHandler(log_path)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

load_dotenv()
NEO_URI = os.getenv('NEO_URI')
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")
DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)
