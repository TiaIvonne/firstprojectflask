import os

# declare an init file to start with flask
#import flask class
from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
   #set configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', default='dev'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    #last line should be return app
    return app
