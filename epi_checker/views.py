from flask import render_template, request
from epi_checker import app
import requests


print(app.config)


@app.route("/", methods=["GET", "POST"])
def hello():
    if request.method == "POST":
        #  url = request.args.get("url", "")
        url = request.form.get("url", "")

        # Process the URL or perform any other necessary actions
        # For demonstration, let's just redirect to the processed URL
        print("url", url)
        x = requests.post(url)
        print(x.text)
        return render_template("index.html", result=x.text)
    else:
        return render_template("index.html", result="")
