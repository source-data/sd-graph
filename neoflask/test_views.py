from unittest.mock import patch
from neoflask.queries import REFEREED_PREPRINTS
from neoflask.views import DEFAULT_PAGE, DEFAULT_PAGESIZE, DEFAULT_PUBLISHER, DEFAULT_REVIEWING_SERVICE
from pytest import fixture

import neoflask

@fixture
def client():
    neoflask.app.config['TESTING'] = True
    client = neoflask.app.test_client()

    yield client

def _assert_collection_refereed_preprints_response_matches(
    make_request,
    **expected_parameters
):
    # we're mocking out the DB call so we don't care about the contents of the returned
    # result, they could be anything.
    expected_refereed_preprints = [{'id': 1}, {'id': 2}]
    with patch(
        'neoflask.views.ask_neo',
        return_value=expected_refereed_preprints,
    ) as mock:
        response = make_request()

        mock.assert_called_once_with(
            REFEREED_PREPRINTS(),
            reviewing_service=expected_parameters.get('reviewing_service', DEFAULT_REVIEWING_SERVICE),
            published_in=expected_parameters.get('published_in', DEFAULT_PUBLISHER),
            pagesize=expected_parameters.get('pagesize', DEFAULT_PAGESIZE),
            page=expected_parameters.get('page', DEFAULT_PAGE),
        )

        assert response.is_json
        actual_refereed_preprints = response.json
        assert expected_refereed_preprints == actual_refereed_preprints

def test_collection_refereed_preprints_get(client):
    """
    Verifies that the getting & filtering refereed preprints works as expected.
    
    Tests `GET /api/v1/collection/refereed-preprints/{reviewing_service}/{published_in}`.
    """
    fixtures = [
        # review service,  publisher, pagesize, page
        ('review commons', 'elife',   None,     None), # no paging parameters
        ('elife',         'lsa',      30,       None), # no page parameter
        ('review commons', 'emboj',   None,     4),    # no pagesize parameter
        ('review commons', 'embor',   100,      10),   # all paging parameter
        ('review commons', 'embor',   20,      3),     # check that caching is aware of paging
    ]
    for reviewing_service, published_in, pagesize, page in fixtures:
        url = f'/api/v1/collection/refereed-preprints/{reviewing_service}/{published_in}'

        paging_parameters = {}
        if pagesize is not None:
            paging_parameters['pagesize'] = pagesize
        if page is not None:
            paging_parameters['page'] = page
        query_param_string = '&'.join([f'{k}={v}' for k, v in paging_parameters.items() if v is not None])
        if query_param_string:
            url += f'?{query_param_string}'

        def make_request():
            return client.get(url)

        _assert_collection_refereed_preprints_response_matches(
            make_request,
            reviewing_service=reviewing_service,
            published_in=published_in,
            **paging_parameters,
        )

def test_collection_refereed_preprints_post(client):
    """
    Verifies that the getting & filtering refereed preprints works as expected.
    
    Tests `POST /api/v1/collection/refereed-preprints`.
    """
    fixtures = [
        # review service,  publisher, pagesize, page
        (None,             None,      None,     None), # no filtering or paging
        ('review commons', None,      None,     None), # no paging, filter by review service
        (None,             'elife',   None,     None), # no paging, filter by publisher
        ('review commons', 'elife',   None,     None), # no paging, filter by review service & publisher
        (None,             None,      100,      None), # no filtering, only pagesize parameter
        ('elife',          'lsa',     30,       None), # no page parameter
        ('review commons', 'emboj',   None,     4),    # no pagesize parameter
        ('review commons', 'embor',   100,      10),   # all filtering & paging parameters
        ('review commons', 'embor',   20,      2),     # check that caching is aware of paging
    ]
    for reviewing_service, published_in, pagesize, page in fixtures:
        url = f'/api/v1/collection/refereed-preprints'

        request_body = {}
        if reviewing_service:
            request_body['reviewing_service'] = reviewing_service
        if published_in:
            request_body['published_in'] = published_in
        if pagesize:
            request_body['pagesize'] = pagesize
        if page:
            request_body['page'] = page

        def make_request():
            return client.post(url, json=request_body)

        _assert_collection_refereed_preprints_response_matches(make_request, **request_body)