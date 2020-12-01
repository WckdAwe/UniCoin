from flask import Flask

app = Flask(__name__)

import UniCoin.web
from UniCoin import decorators

