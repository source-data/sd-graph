from typing import List
import argparse
from tweepy.error import TweepError
from .queries import DELETE_TWEET, ALL_TWEETS, TWEET_BY_ID
from . import DB, TWITTER, logger

'''
Status(_api=<tweepy.api.API object at 0x7fae85eebe10>, _json={'created_at': 'Tue Jul 07 15:32:28 +0000 2020', 'id': 1280525095199531010, 'id_str': '1280525095199531010', 'text': '#RefereedPreprint by @ReviewCommons \nStructures of three MORN repeat proteins and a re-evaluation of the proposed l… https://t.co/w4VmnQylHl', 'truncated': True, 'entities': {'hashtags': [{'text': 'RefereedPreprint', 'indices': [0, 17]}], 'symbols': [], 'user_mentions': [{'screen_name': 'ReviewCommons', 'name': 'Review Commons', 'id': 1158432453473816577, 'id_str': '1158432453473816577', 'indices': [21, 35]}], 'urls': [{'url': 'https://t.co/w4VmnQylHl', 'expanded_url': 'https://twitter.com/i/web/status/1280525095199531010', 'display_url': 'twitter.com/i/web/status/1…', 'indices': [117, 140]}]}, 'source': '', 'in_reply_to_status_id': None, 'in_reply_to_status_id_str': None, 'in_reply_to_user_id': None, 'in_reply_to_user_id_str': None, 'in_reply_to_screen_name': None, 'user': {'id': 1280513399022108677, 'id_str': '1280513399022108677', 'name': 'Early Evidence', 'screen_name': 'EarlyEvidence', 'location': '', 'description': '', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': True, 'followers_count': 0, 'friends_count': 0, 'listed_count': 0, 'created_at': 'Tue Jul 07 14:46:25 +0000 2020', 'favourites_count': 0, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 10, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_image_url_https': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': True, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none'}, 'geo': None, 'coordinates': None, 'place': None, 'contributors': None, 'is_quote_status': False, 'retweet_count': 0, 'favorite_count': 0, 'favorited': False, 'retweeted': False, 'possibly_sensitive': False, 'lang': 'en'}, created_at=datetime.datetime(2020, 7, 7, 15, 32, 28), id=1280525095199531010, id_str='1280525095199531010', text='#RefereedPreprint by @ReviewCommons \nStructures of three MORN repeat proteins and a re-evaluation of the proposed l… https://t.co/w4VmnQylHl', truncated=True, entities={'hashtags': [{'text': 'RefereedPreprint', 'indices': [0, 17]}], 'symbols': [], 'user_mentions': [{'screen_name': 'ReviewCommons', 'name': 'Review Commons', 'id': 1158432453473816577, 'id_str': '1158432453473816577', 'indices': [21, 35]}], 'urls': [{'url': 'https://t.co/w4VmnQylHl', 'expanded_url': 'https://twitter.com/i/web/status/1280525095199531010', 'display_url': 'twitter.com/i/web/status/1…', 'indices': [117, 140]}]}, source='', source_url=None, in_reply_to_status_id=None, in_reply_to_status_id_str=None, in_reply_to_user_id=None, in_reply_to_user_id_str=None, in_reply_to_screen_name=None, author=User(_api=<tweepy.api.API object at 0x7fae85eebe10>, _json={'id': 1280513399022108677, 'id_str': '1280513399022108677', 'name': 'Early Evidence', 'screen_name': 'EarlyEvidence', 'location': '', 'description': '', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': True, 'followers_count': 0, 'friends_count': 0, 'listed_count': 0, 'created_at': 'Tue Jul 07 14:46:25 +0000 2020', 'favourites_count': 0, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 10, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_image_url_https': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': True, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none'}, id=1280513399022108677, id_str='1280513399022108677', name='Early Evidence', screen_name='EarlyEvidence', location='', description='', url=None, entities={'description': {'urls': []}}, protected=True, followers_count=0, friends_count=0, listed_count=0, created_at=datetime.datetime(2020, 7, 7, 14, 46, 25), favourites_count=0, utc_offset=None, time_zone=None, geo_enabled=False, verified=False, statuses_count=10, lang=None, contributors_enabled=False, is_translator=False, is_translation_enabled=False, profile_background_color='F5F8FA', profile_background_image_url=None, profile_background_image_url_https=None, profile_background_tile=False, profile_image_url='http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', profile_image_url_https='https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', profile_link_color='1DA1F2', profile_sidebar_border_color='C0DEED', profile_sidebar_fill_color='DDEEF6', profile_text_color='333333', profile_use_background_image=True, has_extended_profile=True, default_profile=True, default_profile_image=True, following=False, follow_request_sent=False, notifications=False, translator_type='none'), user=User(_api=<tweepy.api.API object at 0x7fae85eebe10>, _json={'id': 1280513399022108677, 'id_str': '1280513399022108677', 'name': 'Early Evidence', 'screen_name': 'EarlyEvidence', 'location': '', 'description': '', 'url': None, 'entities': {'description': {'urls': []}}, 'protected': True, 'followers_count': 0, 'friends_count': 0, 'listed_count': 0, 'created_at': 'Tue Jul 07 14:46:25 +0000 2020', 'favourites_count': 0, 'utc_offset': None, 'time_zone': None, 'geo_enabled': False, 'verified': False, 'statuses_count': 10, 'lang': None, 'contributors_enabled': False, 'is_translator': False, 'is_translation_enabled': False, 'profile_background_color': 'F5F8FA', 'profile_background_image_url': None, 'profile_background_image_url_https': None, 'profile_background_tile': False, 'profile_image_url': 'http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_image_url_https': 'https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', 'profile_link_color': '1DA1F2', 'profile_sidebar_border_color': 'C0DEED', 'profile_sidebar_fill_color': 'DDEEF6', 'profile_text_color': '333333', 'profile_use_background_image': True, 'has_extended_profile': True, 'default_profile': True, 'default_profile_image': True, 'following': False, 'follow_request_sent': False, 'notifications': False, 'translator_type': 'none'}, id=1280513399022108677, id_str='1280513399022108677', name='Early Evidence', screen_name='EarlyEvidence', location='', description='', url=None, entities={'description': {'urls': []}}, protected=True, followers_count=0, friends_count=0, listed_count=0, created_at=datetime.datetime(2020, 7, 7, 14, 46, 25), favourites_count=0, utc_offset=None, time_zone=None, geo_enabled=False, verified=False, statuses_count=10, lang=None, contributors_enabled=False, is_translator=False, is_translation_enabled=False, profile_background_color='F5F8FA', profile_background_image_url=None, profile_background_image_url_https=None, profile_background_tile=False, profile_image_url='http://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', profile_image_url_https='https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png', profile_link_color='1DA1F2', profile_sidebar_border_color='C0DEED', profile_sidebar_fill_color='DDEEF6', profile_text_color='333333', profile_use_background_image=True, has_extended_profile=True, default_profile=True, default_profile_image=True, following=False, follow_request_sent=False, notifications=False, translator_type='none'), geo=None, coordinates=None, place=None, contributors=None, is_quote_status=False, retweet_count=0, favorite_count=0, favorited=False, retweeted=False, possibly_sensitive=False, lang='en')
'''


class Twideleter:

    def __init__(self, db, twitter):
        self.twitter = twitter
        self.db = db

    def delete_one(self, twitter_id):
        # check first that it exists in the database
        if self.db.exists(TWEET_BY_ID(params={'twitter_id': twitter_id})):
            try:
                self.twitter.destroy_status(twitter_id)
            except TweepError as e:
                logger.error(f"twitter_id={twitter_id}: {e}")
            q = DELETE_TWEET(params={'twitter_id': twitter_id})
            db_response = self.db.query(q)
            logger.info(f"deleted twitter status: {twitter_id}")
        else:
            logger.error(f"twitter status: {twitter_id} is not in the database and was NOT deleted on Twitter!")

    def delete_list(self, ids: List):
        for twitter_id in ids:
            self.delete_one(twitter_id)

    def delete_all(self):
        all_tweets_from_db = self.db.query(ALL_TWEETS())
        twitter_ids = [t['tweet']['twitter_id'] for t in all_tweets_from_db]
        self.delete_list(twitter_ids)


def main():
    parser = argparse.ArgumentParser(description="Delete eeb highlights on Twitter.")
    parser.add_argument('ids', nargs="+", help='the id(s) of the tweet or the keyword ALL to delete ALL.')
    args = parser.parse_args()
    ids = args.ids
    t = Twideleter(DB, TWITTER)
    if len(ids) == 1 and ids[0] == 'ALL':
        t.delete_all()
    else:
        t.delete_list(ids)


if __name__ == '__main__':
    main()
