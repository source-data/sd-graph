from collections import namedtuple
from datetime import date, timedelta
from functools import wraps
import pdb
from dateutil.relativedelta import relativedelta
from flask import (
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    Response,
    url_for,
)
from .sitemap import create_sitemap
from .converter import LuceneQueryConverter, ReviewServiceConverter, ListConverter
from .queries import (
    STATS, BY_DOIS, BY_SLUG, FIG_BY_DOI_IDX,
    DESCRIBE_REVIEWING_SERVICES,
    REVIEW_PROCESS_BY_DOI, REVIEW_MATERIAL_BY_ID,
    DOCMAP_BY_DOI, DOCMAPS_FROM_REVSERVICE_IN_INTERVAL,
    DOCMAPS_IN_INTERVAL,
    BY_AUTO_TOPICS, BY_REVIEWING_SERVICE, AUTOMAGIC,
    LUCENE_SEARCH, SEARCH_DOI,
    COVID19, REFEREED_PREPRINTS,
    COLLECTION_NAMES, 
    SUBJECT_COLLECTIONS,
)
from neotools.db import Query
from typing import Dict
import re
from . import app, cache, get_db


DOI_REGEX = re.compile(r'10.\d{4,9}/[-._;()/:A-Z0-9]+$', flags=re.IGNORECASE)

app.url_map.converters['escape_lucene'] = LuceneQueryConverter
app.url_map.converters['service_name'] = ReviewServiceConverter
app.url_map.converters['list'] = ListConverter

def n_months_ago(n):
    n_months_ago = date.today() + relativedelta(months=-n)
    first_day_of_that_month = n_months_ago.replace(day=1)
    return str(first_day_of_that_month)

def ask_neo(query: Query, **kwargs) -> Dict:
    """
    Run a query and return the database results as dictionary with the keys specified in the query.returns list.
    """
    def tx_funct(tx, code, params):
        results = tx.run(code, params)
        data = [r.data(*query.returns) for r in results]  # consuming the data inside the transaction https://neo4j.com/docs/api/python-driver/current/transactions.html
        return data
    # use the map of name of substitution variable in cypher to the name and default value of the var in the request
    for var_in_cypher, var_in_request in query.map.items():
        query.params[var_in_cypher] = kwargs.get(var_in_request['req_param'], var_in_request['default'])
    data = get_db().query_with_tx_funct(tx_funct, query)
    return data


def get_all_dois_and_slugs():
    refereed_preprints = ask_neo(BY_REVIEWING_SERVICE(), limit_date='1900-01-01')
    by_auto_topics = ask_neo(BY_AUTO_TOPICS(), limit_date='1900-01-01')
    automagic = ask_neo(AUTOMAGIC(), limit_date='1900-01-01')
    app.logger.info("gathering all dois")

    dois_and_slugs = []
    for collection in refereed_preprints, by_auto_topics, automagic:
        for sub_collection in collection:
            papers = sub_collection['papers']
            new_dois_and_slugs = [(paper['doi'], paper.get('slug', None)) for paper in papers]
            dois_and_slugs += new_dois_and_slugs
    dois_and_slugs = set(dois_and_slugs)  # remove duplicates
    return dois_and_slugs


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/doi/<path:doi>', methods=['GET'])
def doi_redirect(doi):
    papers = ask_neo(BY_DOIS(), dois=[doi])
    if len(papers) == 0:
        app.logger.debug("tried to redirect DOI %s to slug, no matching paper found", doi)
        return abort(404)
    if len(papers) > 1:
        app.logger.warning("found multiple VizPapers for DOI %s, using first one: %s", doi, papers)

    paper = papers[0]
    slug = paper.get('slug', None)
    if slug:
        app.logger.debug("redirecting DOI %s to slug %s", doi, slug)
        return redirect('/p/' + slug, code=301)
    return render_template('index.html')


# @app.route('/doc')
# def doc():
#     return render_template('doc.html', name='me')


@app.route('/sitemap.xml', methods=['GET'])
@cache.cached()
def sitemap():
    """
    Generate dynamically a sitemap.
    """
    dois_and_slugs = get_all_dois_and_slugs()
    app.logger.info(f"generating sitemap with {len(dois_and_slugs)} links.")
    sitemap = create_sitemap(dois_and_slugs)
    return Response(sitemap, mimetype='text/xml')


@app.route('/api/v1/stats', methods=['GET', 'POST'])
@cache.cached()
def stats():
    app.logger.info(f"show db stats")
    return jsonify(ask_neo(STATS()))


# using routing rather than parameters to provide limit_date so that cache.cached() works properly; memoize would need function params
@app.route('/api/v1/by_auto_topics/', defaults={'limit_date': None}, methods=['GET', 'POST'])
@app.route('/api/v1/by_auto_topics/<limit_date>', methods=['GET', 'POST'])
@cache.cached()
def by_hyp(limit_date):
    if limit_date is None:
        limit_date = n_months_ago(4)
    app.logger.info(f"list by automatic topics with limit {limit_date}")
    return jsonify(ask_neo(BY_AUTO_TOPICS(), limit_date=limit_date))


@app.route('/api/v1/reviewing_services/', methods=['GET', 'POST'])
@cache.cached()
def reviewing_services():
    app.logger.info(f"descriptions of reviewing services")
    return jsonify(ask_neo(DESCRIBE_REVIEWING_SERVICES()))


@app.route('/api/v1/by_reviewing_service/', defaults={'limit_date': '1900-01-01'}, methods=['GET', 'POST'])
@app.route('/api/v1/by_reviewing_service/<limit_date>', methods=['GET', 'POST'])
@cache.cached()
def by_reviewing_service(limit_date):
    app.logger.info(f"list by by_reviewing_service")
    return jsonify(ask_neo(BY_REVIEWING_SERVICE(), limit_date=limit_date))


@app.route('/api/v1/automagic/', defaults={'limit_date': '1900-01-01'}, methods=['GET', 'POST'])
@app.route('/api/v1/automagic/<limit_date>', methods=['GET', 'POST'])
@cache.cached()
def automagic(limit_date):
    app.logger.info(f"list by automagic score")
    return jsonify(ask_neo(AUTOMAGIC(), limit_date=limit_date))


@app.route('/api/v1/doi/<path:doi>', methods=['GET', 'POST'])
@cache.cached()
def by_doi(doi: str):
    app.logger.info(f"lookup doi: {doi}")
    result = ask_neo(BY_DOIS(), dois=[doi])
    return jsonify(result)


@app.route('/api/v1/slug/<path:slug>', methods=['GET', 'POST'])
@cache.cached()
def by_slug(slug: str):
    app.logger.info(f"lookup slug: {slug}")
    result = ask_neo(BY_SLUG(), slug=slug)
    return jsonify(result)


@app.route('/api/v1/dois/', methods=['POST'])
def by_dois():
    if not request.is_json:
        abort(415) # unsupported media type
    if not 'dois' in request.json:
        abort(400) # required parameter is missing
    dois = request.json.get('dois', [])
    published_in = request.json.get('published_in', '')
    num_dois = len(dois)
    dois_info = f'{dois}' if num_dois < 4 else f'["{dois[0]}", "{dois[1]}", ..., "{dois[-1]}"] ({num_dois} in total)'
    app.logger.info(f"lookup dois: {dois_info} {' published in '+published_in if published_in else ''}")

    cache_key = f'/api/v1/dois/{hash(frozenset(dois))}'
    doi_data = cache.get(cache_key)
    if doi_data is None:
        app.logger.debug(f"\t\t cache miss: {cache_key}")
        doi_data = ask_neo(BY_DOIS(), dois=dois, published_in=published_in)
        cache.add(cache_key, doi_data)
    else:
        app.logger.debug(f"\t\t  cache hit: {cache_key}")

    return jsonify(doi_data)


@app.route('/api/v1/reviews/<path:doi>', methods=['GET', 'POST'])
@cache.cached()
def review_by_doi(doi: str):
    app.logger.info(f"review process for doi:{doi}")
    return jsonify(ask_neo(REVIEW_PROCESS_BY_DOI(), doi=doi))


@app.route('/api/v1/review/<path:doi>/<int:n>', methods=['GET', 'POST'])
@cache.cached()
def review_by_doi_n(doi: str, n: int):
    app.logger.info(f"review #{n} for doi:{doi}")
    j = ask_neo(REVIEW_PROCESS_BY_DOI(), doi=doi)
    try:
        j = j[0].get('review_process', []).get('reviews', [])
        j = j[n]
    except IndexError:
        j = {}
    return jsonify(j)


@app.route('/api/v1/response/<path:doi>', methods=['GET', 'POST'])
@cache.cached()
def response_by_doi(doi: str):
    app.logger.info(f"response for doi:{doi}")
    j = ask_neo(REVIEW_PROCESS_BY_DOI(), doi=doi)
    j = j[0].get('review_process', []).get('response', [])
    return jsonify(j)


@app.route('/api/v1/figure', methods=['GET', 'POST'])
def fig_by_doi_idx():
    app.logger.info(f"figure {request.args.get('position_idx')} from {request.args.get('doi')}")
    return jsonify(ask_neo(FIG_BY_DOI_IDX(), **request.args))


# <escape_lucene:search_string> triggers the use of converter.LuceneQueryConverter to quotes Lucene search strings
@app.route('/api/v1/search/<escape_lucene:search_string>', methods=['GET'])
# using <path:search_string> to match route when doi is searched
@app.route('/api/v1/search/<path:search_string>', methods=['GET'])
@cache.cached()
def search(search_string: str):
    search_string = search_string.strip()
    doi = DOI_REGEX.search(search_string)
    if doi is not None:
        doi = doi.group(0)
        app.logger.info(f"search doi: '{doi}'")
        results = ask_neo(SEARCH_DOI(), search_string=doi)
    else:
        app.logger.info(f"search text: '{search_string}'")
        results = ask_neo(LUCENE_SEARCH(), search_string=search_string)
    return jsonify(results)


@app.route('/api/v1/collection/covid19', methods=['GET', 'POST'])
@cache.cached()
def covid19():
    return jsonify(ask_neo(COVID19()))

def _fetch_refereed_preprints(reviewing_service, published_in, pagesize, page):
    app.logger.info(
        "refereed preprints from '%s' published in '%s' (page %s of size %s)",
        reviewing_service,
        published_in,
        page,
        pagesize,
    )
    return jsonify(
        ask_neo(
            REFEREED_PREPRINTS(),
            reviewing_service=reviewing_service,
            published_in=published_in,
            pagesize=int(pagesize),
            page=int(page),
        )
    )

PagingParameters = namedtuple('PagingParameters', ['page', 'pagesize'])
"""The container for the paging parameters, i.e. the page number and page size."""

DEFAULT_PAGESIZE = 20
DEFAULT_PAGE = 0
def paged(view_func):
    """
    Decorator that simplifies paged views.

    Reads parameters named `pagesize` and `page` from the request data and puts their
    values into a dict called `paging` on the request object. The values can be
    retrieved like so: `request.paging['pagesize'], request.paging['page']`.
    If one or both parameters are not present, default values are used.

    For GET requests, the parameters are retrieved from the query string.
    For POST requests with JSON request bodies, they are read from the request body.
    In any other case a warning is logged and the defaults are used.
    """

    param_name_pagesize = 'pagesize'
    param_name_page = 'page'

    @wraps(view_func)
    def inner(*args, **kwargs):
        if request.method == 'GET':
            param_dict = request.args
        elif request.method == 'POST' and request.is_json:
            param_dict = request.json
        else:
            app.logger.warning(
                'Failed to retrieve paging parameters for route %s: not implemented for request method %s or mime type %s',
                request.url,
                request.method,
                request.mimetype,
            )
            param_dict = {}

        request.paging = PagingParameters(
            page=param_dict.get(param_name_page, DEFAULT_PAGE),
            pagesize=param_dict.get(param_name_pagesize, DEFAULT_PAGESIZE),
        )

        return view_func(*args, **kwargs)

    return inner

def paging_aware_cache_key():
    """
    Function to generate a paging-aware cache key.

    Use it as the `make_cache_key` parameter to @cached and in conjunction with @paged.

    Adds the paging parameters set by the @paged decorator to the cache key. Otherwise,
    requesting the same URL with different paging parameters returns the first, cached,
    result.
    """
    return f'view/{request.path}/page-{hash(request.paging)}'

DEFAULT_REVIEWING_SERVICE = ''
DEFAULT_PUBLISHER = ''

@app.route(
    '/api/v1/collection/refereed-preprints/<service_name:reviewing_service>/<published_in>',
    methods=['GET'],
)
@paged
@cache.cached(key_prefix=paging_aware_cache_key)
def refereed_preprints_get(reviewing_service, published_in):
    """
    Returns all refereed preprints that were reviewed by `reviewing_service` and
    published in `published_in`.
    
    Results are sorted by publication date of the preprint and paged. Use the query
    parameters `pagesize` and `page` to adjust the paging:
    /api/v1/collection/refereed-preprints/reviewcommons/elife?pagesize=100&page=3

    For more control, e.g. not filtering by reviewing service or publisher, use the POST
    version of this route.
    """
    return _fetch_refereed_preprints(
        reviewing_service=reviewing_service,
        published_in=published_in,
        pagesize=request.paging.pagesize,
        page=request.paging.page,
    )

@app.route('/api/v1/collection/refereed-preprints', methods=['GET'])
@cache.cached()
def refereed_preprints_get_all():
    """
    Returns all refereed preprints sorted by publication date of the preprint.

    For more control, e.g. not filtering by reviewing service or publisher, use the POST
    version of this route.
    """
    return _fetch_refereed_preprints(
        reviewing_service=DEFAULT_REVIEWING_SERVICE,
        published_in=DEFAULT_PUBLISHER,
        pagesize=10 ** 7,
        page=DEFAULT_PAGE,
    )

@app.route('/api/v1/collection/refereed-preprints', methods=['POST'])
@paged
def refereed_preprints_post():
    """
    Returns all refereed preprints. Results can be filtered by reviewing service and
    publisher.

    The request body must be JSON, or empty. If empty, all refereed preprints are returned.
    The results can be filtered by which reviewing service reviewed them (`reviewing_service`)
    and/or where they were published (`published_in`):
    `{ "reviewing_service": "review commons", "published_in": "Life Science Alliance" }`.

    Results are sorted by publication date of the preprint and paged. Use the parameters
    `pagesize` and `page` to adjust the paging: `{ "pagesize": 100, "page": 3 }`
    """
    if not request.is_json:
        abort(415) # unsupported media type
    return _fetch_refereed_preprints(
        reviewing_service=request.json.get('reviewing_service', DEFAULT_REVIEWING_SERVICE),
        published_in=request.json.get('published_in', DEFAULT_PUBLISHER),
        pagesize=request.paging.pagesize,
        page=request.paging.page,
    )

@app.route('/api/v1/collection/<subject>', methods=['GET', 'POST'])
@cache.cached()
def subject_collection(subject: str):
    app.logger.info(f"subject collection for subject: '{subject}'")
    return jsonify(ask_neo(SUBJECT_COLLECTIONS(), subject=subject))


@app.route('/api/v1/subjects', methods=['GET', 'POST'])
@cache.cached()
def subjects():
    app.logger.info(f"subjects names")
    return jsonify(ask_neo(COLLECTION_NAMES()))


@app.route('/api/v2/review_material/<int:node_id>', methods=['GET', 'POST'])
@cache.cached()
def review_material_by_id(node_id: int):
    app.logger.info(f"review material for id {node_id}")
    root = url_for('root', _external=True)
    j = ask_neo(REVIEW_MATERIAL_BY_ID(), node_id=node_id, root=root)
    return jsonify(j)


@app.route('/api/v2/review_process/<path:doi>', methods=['GET', 'POST'])
@app.route('/api/v2/docmap/<path:doi>', methods=['GET', 'POST'])
@cache.cached()
def docmap_semantic_doi(doi: str):
    app.logger.info(f"docmap for id {doi}")
    root = url_for('root', _external=True)
    j = ask_neo(DOCMAP_BY_DOI(), doi=doi, root=root)
    return jsonify(j)

def do_paginated_docmap_query(query, page=0, page_size=100, **kwargs):
    if page < 0:
        abort(400) # pagination paramater must be 0 or greater

    offset = page * page_size
    root = url_for('root', _external=True)

    result = ask_neo(
        query,
        root=root,
        offset=offset,
        page_size=page_size,
        **kwargs,
    )

    return jsonify(result)

@app.route('/api/v2/<service_name:reviewing_service>/docmap/<start_date>/<end_date>/<int:pagination>', methods=['GET', 'POST'])
def docmaps_from_revservice_in_interval(reviewing_service: str, start_date: str, end_date: str, pagination: int):
    app.logger.info(f"Getting docmaps for reviewing service \"{reviewing_service}\" from {start_date} to {end_date}, page {pagination}")
    return do_paginated_docmap_query(
        DOCMAPS_FROM_REVSERVICE_IN_INTERVAL(),
        reviewing_service=reviewing_service,
        start_date=start_date,
        end_date=end_date,
        page=pagination,
    )

@app.route('/api/v2/docmap/<start_date>/<end_date>/<int:pagination>', methods=['GET', 'POST'])
def docmaps_in_interval(start_date: str, end_date: str, pagination: int):
    app.logger.info(f"Getting docmaps from {start_date} to {end_date}, page {pagination}")
    return do_paginated_docmap_query(
        DOCMAPS_IN_INTERVAL(),
        start_date=start_date,
        end_date=end_date,
        page=pagination,
    )

@app.route('/api/v2/<service_name:reviewing_service>/docmap/<int:days>d/<int:pagination>', methods=['GET', 'POST'])
def docmaps_from_revservice_in_last_days(reviewing_service: str, days: int, pagination: int):
    app.logger.info(f"Getting docmaps for reviewing service \"{reviewing_service}\" with reviews in the last {days} days, page {pagination}")
    # The Docmap query is exclusive for the end of the interval. We want any reviews published today so add a day here.
    end_date = date.today() + timedelta(days=1)
    # With this start date we get any reviews published today and in the last n-1 days, so reviews from a total of n days.
    start_date = end_date - timedelta(days=days)
    return do_paginated_docmap_query(
        DOCMAPS_FROM_REVSERVICE_IN_INTERVAL(),
        reviewing_service=reviewing_service,
        start_date=str(start_date),
        end_date=str(end_date),
        page=pagination,
    )

# @app.route('/api/v2/<reviewing_service>/docmap/<int:n_most_recent>/<int:pagination>', methods=['GET', 'POST'])

# date of docmap creation and date of docmap update. filter on publishing data or on docmap creation date.