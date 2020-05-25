import os
import argparse
from flask import Flask, request, render_template, Response, flash, redirect, send_from_directory, url_for, make_response
from .search import Engine
from . import DB, app

from flask_cors import CORS
# CORS(app)
# CORS(app, resources={r"/*": {"origins": "ec2-18-185-121-134.eu-central-1.compute.amazonaws.com"}})
# CORS(app, resources={r"/*": {"origins": "*"}})
# CORS(app, resources={r"/*": {"origins": "sdash.laravel"}})


ASKNEO = Engine(DB)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/doc')
def doc():
    return render_template('doc.html', name='me')


@app.route('/api/v1/by_molecule', methods=['GET', 'POST'])
def by_molecule():
    app.logger.info(f"list by molecule")
    return R(ASKNEO.by_molecule(request))


@app.route('/api/v1/by_method', methods=['GET', 'POST'])
def by_method():
    app.logger.info(f"list by method")
    return R(ASKNEO.by_method(request))


@app.route('/api/v1/by_hyp', methods=['GET', 'POST'])
def by_hyp():
    app.logger.info(f"list by hypotheses")
    return R(ASKNEO.by_hyp(request))


@app.route('/api/v1/automagic', methods=['GET', 'POST'])
def automagic():
    app.logger.info(f"list by automagic score")
    return R(ASKNEO.automagic(request))


@app.route('/api/v1/doi/<path:doi>', methods=['GET', 'POST'])
def by_doi(doi: str):
    app.logger.info(f"search doi:{doi}")
    return R(ASKNEO.by_doi(doi=doi))


@app.route('/api/v1/figure', methods=['GET', 'POST'])
def fig_by_doi_idx():
    app.logger.info(f"figure {request.args.get('position_idx')} from {request.args.get('doi')}")
    return R(ASKNEO.fig_by_doi_idx(request))


@app.route('/api/v1/panel/<int:id>', methods=['GET', 'POST'])
def panel_by_neo_id(id):
    app.logger.info(f"panel {id}")
    return R(ASKNEO.panel_by_neo_id(id=id))


@app.route('/api/v1/search/', methods=['GET'])
def entity():
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


def R(response):
    mimetype = 'application/json'
    return Response(response, mimetype=mimetype)
