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


@app.route('/api/v1/doi/<path:doi>', methods=['GET', 'POST'])
def by_doi(doi: str):
    app.logger.info(f"search doi:{doi}")
    return R(ASKNEO.by_doi(doi))


@app.route('/api/v1/search/', methods=['GET'])
def entity():
    app.logger.info(f"search '{request.args.get('query')}'")
    return R(ASKNEO.search(request))


def R(response):
    mimetype = 'application/json'
    return Response(response, mimetype=mimetype)

