from flask import request, render_template, Response, redirect
from .search import Engine
from . import DB, app, cache


ASKNEO = Engine(DB)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/doc')
def doc():
    return render_template('doc.html', name='me')


@app.route('/api/v1/stats', methods=['GET', 'POST'])
@cache.cached()
def stats():
    app.logger.info(f"show db stats")
    return R(ASKNEO.stats(request))


@app.route('/api/v1/by_molecule', methods=['GET', 'POST'])
@cache.cached()
def by_molecule():
    app.logger.info(f"list by molecule")
    return R(ASKNEO.by_molecule(request))


@app.route('/api/v1/by_method', methods=['GET', 'POST'])
@cache.cached()
def by_method():
    app.logger.info(f"list by method")
    return R(ASKNEO.by_method(request))


@app.route('/api/v1/by_hyp', methods=['GET', 'POST'])
@cache.cached()
def by_hyp():
    app.logger.info(f"list by hypotheses")
    return R(ASKNEO.by_hyp(request))


@app.route('/api/v1/automagic', methods=['GET', 'POST'])
@cache.cached()
def automagic():
    app.logger.info(f"list by automagic score")
    return R(ASKNEO.automagic(request))


@app.route('/api/v1/doi/<path:doi>', methods=['GET', 'POST'])
def by_doi(doi: str):
    app.logger.info(f"search doi:{doi}")
    return R(ASKNEO.by_doi(doi=doi))

@app.route('/api/v1/review/<path:doi>', methods=['GET', 'POST'])
def review_by_doi(doi: str):
    app.logger.info(f"review for doi:{doi}")
    return R(ASKNEO.review_by_doi(doi=doi))

@app.route('/api/v1/figure', methods=['GET', 'POST'])
def fig_by_doi_idx():

    app.logger.info(f"figure {request.args.get('position_idx')} from {request.args.get('doi')}")
    return R(ASKNEO.fig_by_doi_idx(request))


@app.route('/api/v1/panel/<int:id>', methods=['GET', 'POST'])
def panel_by_neo_id(id):
    app.logger.info(f"panel {id}")
    return R(ASKNEO.panel_by_neo_id(id=id))


@app.route('/api/v1/search/', methods=['GET'])
# @cache.cached()
def search():
    app.logger.info(f"search '{request.args.get('query')}'")
    return R(ASKNEO.search(request))


@app.route('/api/v1/smartfigure/<id>', methods=['GET', 'POST'])
def smartfigure(id: str):
    smartfigure_url = f'https://search.sourcedata.io/panel/{id}'
    return redirect(smartfigure_url)


@app.route('/api/v1/summary/<panel_id>', methods=['GET', 'POST'])
def panel_summary(panel_id: str):
    return R(ASKNEO.panel_summary(panel_id=panel_id))


@app.route('/api/v1/collection/covid19', methods=['GET', 'POST'])
def covid19():
    return R(ASKNEO.covid19(request))


@app.route('/api/v1/collection/refereed-preprints', methods=['GET', 'POST'])
def refereed_preprints():
    return R(ASKNEO.refereed_preprints(request))


def R(response):
    mimetype = 'application/json'
    return Response(response, mimetype=mimetype)
