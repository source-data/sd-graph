from datetime import date, timedelta
from flask import (
    abort,
    jsonify,
    render_template,
    request,
    Response,
    url_for,
)
from .sitemap import create_sitemap
from .converter import LuceneQueryConverter, ReviewServiceConverter
from .queries import (
    STATS, BY_DOI, FIG_BY_DOI_IDX,
    DESCRIBE_REVIEWING_SERVICES,
    REVIEW_PROCESS_BY_DOI, REVIEW_MATERIAL_BY_ID,
    DOCMAP_BY_DOI, DOCMAPS_FROM_REVSERVICE_IN_INTERVAL,
    DOCMAPS_IN_INTERVAL,
    BY_AUTO_TOPICS, BY_REVIEWING_SERVICE, AUTOMAGIC,
    LUCENE_SEARCH, SEARCH_DOI,
    COVID19, REFEREED_PREPRINTS,
    COLLECTION_NAMES, SUBJECT_COLLECTIONS,
)
from neotools.db import Query
from typing import Dict
import re
from . import DB, app, cache


DOI_REGEX = re.compile(r'10.\d{4,9}/[-._;()/:A-Z0-9]+$', flags=re.IGNORECASE)

app.url_map.converters['escape_lucene'] = LuceneQueryConverter
app.url_map.converters['service_name'] = ReviewServiceConverter

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
    data = DB.query_with_tx_funct(tx_funct, query)
    return data


def get_all_dois():

    refereed_preprints = ask_neo(BY_REVIEWING_SERVICE(), limit_date='1900-01-01')
    by_auto_topics = ask_neo(BY_AUTO_TOPICS(), limit_date='1900-01-01')
    automagic = ask_neo(AUTOMAGIC(), limit_date='1900-01-01')
    app.logger.info("gathering all dois")
    dois = []
    for collection in refereed_preprints:
        papers = collection['papers']
        new_dois = [paper['doi'] for paper in papers]
        dois += new_dois
    for collection in by_auto_topics:
        papers = collection['papers']
        new_dois = [paper['doi'] for paper in papers]
        dois += new_dois
    for collection in automagic:
        papers = collection['papers']
        new_dois = [paper['doi'] for paper in papers]
        dois += new_dois
    dois = set(dois)  # remove duplicates
    return dois


@app.route('/')
def root():
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
    dois = get_all_dois()
    app.logger.info(f"generating sitemap with {len(dois)} links.")
    sitemap = create_sitemap(dois)
    return Response(sitemap, mimetype='text/xml')


@app.route('/api/v1/stats', methods=['GET', 'POST'])
@cache.cached()
def stats():
    app.logger.info(f"show db stats")
    return jsonify(ask_neo(STATS()))


# using routing rather than parameters to provide limit_date so that cache.cached() works properly; memoize would need function params
@app.route('/api/v1/by_auto_topics/', defaults={'limit_date': '1900-01-01'}, methods=['GET', 'POST'])
@app.route('/api/v1/by_auto_topics/<limit_date>', methods=['GET', 'POST'])
@cache.cached()
def by_hyp(limit_date):
    app.logger.info(f"list by automatic topics")
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
    return jsonify(ask_neo(BY_DOI(), doi=doi))


@app.route('/api/v1/dois/', methods=['POST'])
def by_dois():
    if not request.is_json:
        abort(415) # unsupported media type
    if not 'dois' in request.json:
        abort(400) # required parameter is missing
    dois = request.json.get('dois', [])
    app.logger.info(f"lookup dois: {dois}")
    response = []
    for doi in dois:
        cache_key = f'/api/v1/dois/{doi}'
        doi_data = cache.get(cache_key)
        if doi_data is None:
            app.logger.info(f"\t\t cache miss: {doi}")
            doi_data = ask_neo(BY_DOI(), doi=doi)[0]
            cache.add(cache_key, doi_data)
        else:
            app.logger.info(f"\t\t  cache hit: {doi}")
        response.append(doi_data)
    return jsonify(response)


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


@app.route('/api/v1/collection/refereed-preprints', methods=['GET', 'POST'])
@cache.cached()
def refereed_preprints():
    return jsonify(ask_neo(REFEREED_PREPRINTS()))


@app.route('/api/v1/subjects', methods=['GET', 'POST'])
@cache.cached()
def subjects():
    app.logger.info(f"subjects names")
    return jsonify(ask_neo(COLLECTION_NAMES()))


@app.route('/api/v1/collection/<subject>', methods=['GET', 'POST'])
@cache.cached()
def subject_collection(subject: str):
    app.logger.info(f"collection '{subject}'")
    return jsonify(ask_neo(SUBJECT_COLLECTIONS(), subject=subject))


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