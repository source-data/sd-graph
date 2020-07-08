import os
import logging
import sys
from pathlib import Path
from dotenv import load_dotenv
from neotools.db import Instance
from tweepy import API, OAuthHandler

# create logger
logger = logging.getLogger('twhighlight logger')
logger.setLevel(logging.DEBUG)
log_dir = Path('twitter/log')
log_file = Path('twitter.log')
if not log_dir.exists():
    Path(log_dir).mkdir(parents=True)
log_path = log_dir / log_file
ch = logging.FileHandler(log_path)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(formatter)
logger.addHandler(consoleHandler)

load_dotenv()
NEO_URI = os.getenv('NEO_URI')
NEO_USERNAME = os.getenv("NEO_USERNAME")
NEO_PASSWORD = os.getenv("NEO_PASSWORD")
DB = Instance(NEO_URI, NEO_USERNAME, NEO_PASSWORD)

EEB_PUBLIC_API = os.getenv("EEB_PUBLIC_API")

TWITTER_CONSUMER_KEY = os.getenv('TWITTER_CONSUMER_KEY')
TWITTER_CONSUMER_SECRET = os.getenv('TWITTER_CONSUMER_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')


auth = OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
auth.set_access_token(TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET)
TWITTER = API(auth)
