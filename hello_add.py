"""Flask addition exercise from Lab 7."""

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/add", methods=["POST"])
def add():
    data = request.get_json()
    return jsonify({"sum": data["a"] + data["b"]})
