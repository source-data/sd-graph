import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from . import SD_API_USERNAME, SD_API_PASSWORD


def requests_retry_session(
    retries=3,
    backoff_factor=0.3,
    status_forcelist=(500, 502, 504),
    session=None,
):
    # from  https://www.peterbe.com/plog/best-practice-with-retries-with-requests
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


SESSION = requests.Session()
SESSION.auth = (SD_API_USERNAME, SD_API_PASSWORD)
# s.headers.update({'Accept': 'application/json'})

SESSION_RETRY = requests_retry_session(
    session=SESSION
)
