import json
from pathlib import Path


from flask import Flask, request
from flask_basicauth import BasicAuth
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from ..task1.nest import group_by_key


path = Path('.').resolve()
app = Flask(__name__)

with open(f'{path}/etc/config.yaml') as config:
    app.config.update(yaml.load(config.read(), Loader=Loader))

basic_auth = BasicAuth(app)


@app.route("/", methods=['POST'])
def nest():
    """
    Receive data via post, nest object according to passed keys, e.g.
    {
        "data": [{..}, {...}, ...],  # items
        "nesting_keys": ["key1", "key2", ...]
    } ->  {...}  # nested obj
    """
    data = group_by_key(request.json['data'], request.json['nesting_keys'])
    return json.dumps(data)
