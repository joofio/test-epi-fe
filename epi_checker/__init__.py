"""Flask app for starting server."""

from flask import Flask

app = Flask(__name__)


import epi_checker.views
