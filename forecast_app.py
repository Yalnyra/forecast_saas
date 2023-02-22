import datetime as dt
import json
import requests
from flask import Flask, jsonify, request

#API TOKEN
API_TOKEN = ""

#API KEY
RSA_API_KEY = ""

app = Flask(__name__)

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def get_historic_data(latitude: float, longitude: float, date: str, **kwargs):
    url_base = "https://archive-api.open-meteo.com/v1"
    url_endpoint = "archive"
    url_attrs = {"latitude": latitude, "longitude": longitude, "start_date": date, "end_date": date + 1}.append(kwaargs)
    return None

@app.route("/")
def home():
    return '<h1>Eugen Vinokur</h1><p><h2>KMA SaaS WS! For API please visit: </h2><a href="https://open-meteo.com/">link</a></p>'
