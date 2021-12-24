from flask import Flask, render_template, request
import SatelliteWeatherDataCollector

app = Flask(__name__)


@app.route("/")
def table():
    return render_template("index.html", data=SatelliteWeatherDataCollector.get_satellite_data("0", "0"))


@app.route("/", methods=["POST"])
def update_table():
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    return render_template("index.html", data=SatelliteWeatherDataCollector.get_data(latitude, longitude))
