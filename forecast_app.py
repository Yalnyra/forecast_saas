import datetime as dt
import json
import requests
from flask import Flask, jsonify, request

# API TOKEN
API_TOKEN = ""

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


def get_location(location: str, country: str, count=20):
    url_endpoint = "https://geocoding-api.open-meteo.com/v1/search"
    url = f"{url_endpoint}?name={location}&count={count}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers)
    data = json.loads(response.text)
    if data["results"]:
        cities = data["results"]
        for city in cities:
            if city["name"].upper() == location.upper() and city["country"].upper() == country.upper():
                return {
                    "location": city["name"],
                    "latitude": city["latitude"],
                    "longitude": city["longitude"],
                    "elevation": city["elevation"],
                    "country_code": city["country_code"],
                    "country": city["country"]
                }
    raise InvalidUsage(f"information for the city {location}, {country} not found", status_code=404)


def get_historic_data(latitude: float, longitude: float, date: str, **kwargs):
    url_base = "https://archive-api.open-meteo.com/v1"
    url_endpoint = "archive"
    url = f"{url_base}/{url_endpoint}" \
          f"?latitude={latitude}" \
          f"&longitude={longitude}" \
          f"&start_date={date}" \
          f"&end_date={date}"
    if kwargs:
        for keys in kwargs.keys():
            url += f"&{keys}={kwargs[keys]}"

    payload = {}
    headers = {}

    response = requests.request("GET", url, headers=headers)
    return json.loads(response.text)


@app.route("/")
def home():
    return '<h1>Eugen Vinokur</h1>' \
           '<p><h2>KMA SaaS WS! For API please visit: </h2>' \
           '<a href="https://open-meteo.com/">link</a></p>'


def validate_date(raw_date: str):
    date = raw_date.split('-')
    if len(date) != 3:
        raise InvalidUsage("date must have 3 digits separated by '-' ", status_code=403)
    for category in date:
        if not category.isdigit():
            raise InvalidUsage(f"{category} in {raw_date} is not a number ", status_code=403)
    year = int(date[0])
    if year < 1959:
        raise InvalidUsage("no information about weather before year 1959 ", status_code=403)
    month = int(date[1])
    day = int(date[2])
    if (1, 3, 5, 7, 8, 10, 12).__contains__(month) and 1 <= day <= 31:
        return True
    elif (4, 6, 9, 11).__contains__(month) and 1 <= day <= 30:
        return True
    elif month == 2 and 1 <= day <= 28:
        return True
    elif month == 2 and day == 29 and year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
        return True
    raise InvalidUsage("wrong day and month format ", status_code=403)


@app.route("/api/v1/weather/",
           methods=["POST"], )
def forecast_endpoint():
    request_time = dt.datetime.now()
    data = request.get_json()

    if data.get("token") is None:
        raise InvalidUsage("token is required", status_code=400)

    token = data.get("token")

    if token != API_TOKEN:
        raise InvalidUsage("wrong API token", status_code=403)

    if data.get("requester_name") is None:
        raise InvalidUsage("requester_name is required", status_code=400)

    # later add check for requester_name to match format: Name Surname
    requester_name = data.get("requester_name")

    if data.get("location") is None:
        raise InvalidUsage("location is required", status_code=400)

    location_name = str(data.get("location")).strip().split(",")

    if len(location_name) < 2:
        raise InvalidUsage("location must contain city and country", status_code=403)

    location = get_location(location_name[0], location_name[1])

    if data.get("date") is None:
        raise InvalidUsage("date is required", status_code=400)

    date = str(data.get("date")).strip()

    validate_date(date)

    result = {
        "requester_name": requester_name,
        "timestamp": request_time.isoformat(),
        "location": f"{location['location']}, {location['country']} location{'country_code'}",
        "date": date,
    }

    return result
