import json
from pathlib import Path


from flask import Flask, request
from flask_basicauth import BasicAuth
from flask_mysqldb import MySQL
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from ..task1.nest import group_by_key
from .deposit_api import deposit_api

path = Path('.').resolve()
app = Flask(__name__)
with open(f'{path}/etc/task3_config.yaml') as config:
    app.config.update(yaml.load(config.read(), Loader=Loader))

db = MySQL(app)
app.config.db = db
basic_auth = BasicAuth(app)

app.register_blueprint(deposit_api, url_prefix='/api/v1/deposit')
