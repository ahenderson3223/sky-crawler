from flask import Flask, render_template
import IssScraper

app = Flask(__name__)


@app.route("/")
def table():
    return render_template("index.html", data=IssScraper.scrape("41", "78"))
