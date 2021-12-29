from flask import Flask, render_template, request
import SatelliteWeatherDataCollector

app = Flask(__name__)


@app.route("/")
def table():
    return render_template("index.html", data=SatelliteWeatherDataCollector.get_data("0", "0", "ISS"))


@app.route("/", methods=["POST"])
def update_table():
    # TODO: show previously chosen satellite after page redirects
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    satellite = request.form.get("satelliteDropdown")
    return render_template("index.html", data=SatelliteWeatherDataCollector.get_data(latitude, longitude, satellite))
