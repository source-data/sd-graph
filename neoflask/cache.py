from flask_caching import Cache

cache = Cache(config={
    'CACHE_DEFAULT_TIMEOUT': 365 * 24 * 60 * 60,
    'CACHE_KEY_PREFIX': __name__,
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': 'redis',
    'CACHE_REDIS_PORT': '6379',
})


def init_cache(app):
    cache.init_app(app)
    with app.app_context():
        cache.clear()
