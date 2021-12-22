from flask import Flask, render_template, request
import IssScraper

app = Flask(__name__)


@app.route("/")
def table():
    return render_template("index.html", data=IssScraper.scrape("0", "0"))


@app.route("/", methods=["POST"])
def update_table():
    latitude = request.form["latitude"]
    longitude = request.form["longitude"]
    return render_template("index.html", data=IssScraper.scrape(latitude, longitude))
