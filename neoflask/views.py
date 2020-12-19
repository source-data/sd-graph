from flask import request, render_template, jsonify, Response
from .engine import Engine
from .sitemap import create_sitemap
from . import DB, app, cache
from .converter import LuceneQueryConverter
from flask_cors import cross_origin

app.url_map.converters['escape_lucene'] = LuceneQueryConverter

ASKNEO = Engine(DB)


def get_all_dois():
    refereed_preprints = ASKNEO.by_reviewing_service(limit_date='1900-01-01')
    by_auto_topics = ASKNEO.by_auto_topics(limit_date='1900-01-01')
    automagic = ASKNEO.automagic(limit_date='1900-01-01')
    app.logger.info(automagic)
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
    return jsonify(ASKNEO.stats(request))


# using routing rather than parameters to provide limit_date so that cache.cached() works properly; memoize would need function params
@app.route('/api/v1/by_auto_topics/', defaults={'limit_date': '1900-01-01'}, methods=['GET', 'POST'])
@app.route('/api/v1/by_auto_topics/<limit_date>', methods=['GET', 'POST'])
@cache.cached()
def by_hyp(limit_date):
    app.logger.info(f"list by automatic topics")
    return jsonify(ASKNEO.by_auto_topics(limit_date=limit_date))


@app.route('/api/v1/by_reviewing_service/', defaults={'limit_date': '1900-01-01'}, methods=['GET', 'POST'])
@app.route('/api/v1/by_reviewing_service/<limit_date>', methods=['GET', 'POST'])
@cache.cached()
def by_reviewing_service(limit_date):
    app.logger.info(f"list by by_reviewing_service")
    return jsonify(ASKNEO.by_reviewing_service(limit_date=limit_date))


@app.route('/api/v1/automagic/', defaults={'limit_date': '1900-01-01'}, methods=['GET', 'POST'])
@app.route('/api/v1/automagic/<limit_date>', methods=['GET', 'POST'])
@cache.cached()
def automagic(limit_date):
    app.logger.info(f"list by automagic score")
    return jsonify(ASKNEO.automagic(limit_date=limit_date))


@app.route('/api/v1/doi/<path:doi>', methods=['GET', 'POST'])
@cache.cached()
def by_doi(doi: str):
    app.logger.info(f"search doi:{doi}")
    return jsonify(ASKNEO.by_doi(doi=doi))


@app.route('/api/v1/dois/', methods=['POST'])
def by_dois():
    dois = request.json['dois']
    app.logger.info(f"search dois:{dois}")
    response = []
    for doi in dois:
        cache_key = f'/api/v1/dois/{doi}'
        doi_data = cache.get(cache_key)
        if doi_data is None:
            app.logger.info(f"\t\t cache miss: {doi}")
            doi_data = ASKNEO.by_doi(doi=doi)[0]
            cache.add(cache_key, doi_data)
        else:
            app.logger.info(f"\t\t  cache hit: {doi}")
        response.append(doi_data)
    return jsonify(response)


@app.route('/api/v1/review/<path:doi>', methods=['GET', 'POST'])
@cache.cached()
def review_by_doi(doi: str):
    app.logger.info(f"review for doi:{doi}")
    return jsonify(ASKNEO.review_by_doi(doi=doi))


@app.route('/api/v1/figure', methods=['GET', 'POST'])
def fig_by_doi_idx():
    app.logger.info(f"figure {request.args.get('position_idx')} from {request.args.get('doi')}")
    return jsonify(ASKNEO.fig_by_doi_idx(request))


# @app.route('/api/v1/panel/<int:id>', methods=['GET', 'POST'])
# def panel_by_neo_id(id):
#     app.logger.info(f"panel {id}")
#     return jsonify(ASKNEO.panel_by_neo_id(id=id))


@app.route('/api/v1/search/<escape_lucene:query>', methods=['GET'])
@cache.cached()
def search(query: str):
    app.logger.info(f"search '{query}'")
    return jsonify(ASKNEO.search(query=query))


# @app.route('/api/v1/smartfigure/<id>', methods=['GET', 'POST'])
# def smartfigure(id: str):
#     smartfigure_url = f'https://search.sourcedata.io/panel/{id}'
#     return redirect(smartfigure_url)


# @app.route('/api/v1/summary/<panel_id>', methods=['GET', 'POST'])
# def panel_summary(panel_id: str):
#     return jsonify(ASKNEO.panel_summary(panel_id=panel_id))


@app.route('/api/v1/collection/covid19', methods=['GET', 'POST'])
@cache.cached()
def covid19():
    return jsonify(ASKNEO.covid19(request))


@app.route('/api/v1/collection/refereed-preprints', methods=['GET', 'POST'])
@cache.cached()
def refereed_preprints():
    return jsonify(ASKNEO.refereed_preprints(request))


@app.route('/api/v1/subjects', methods=['GET', 'POST'])
@cache.cached()
def subjects():
    app.logger.info(f"subjects names")
    return jsonify(ASKNEO.subjects(request))


@app.route('/api/v1/collection/<subject>', methods=['GET', 'POST'])
@cache.cached()
def subject_collection(subject: str):
    app.logger.info(f"collection '{subject}'")
    return jsonify(ASKNEO.subject_collection(subject))
