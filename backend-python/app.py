import csv
import zipfile

import click
import flask
from flask import json

def create_app(config_filename):
    app = flask.Flask(__name__)

    # Ensure a connection can 
    import database
    with app.app_context():
        database.init_app(app)

    import movies
    movies.init_app(app)

    import cli
    cli.init_app(app)
    
    return app