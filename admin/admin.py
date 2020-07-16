from flask import Blueprint, render_template, jsonify, url_for, redirect, request
import datetime, string
from database import mongo
from random import *


app = Blueprint('admin', __name__,template_folder='templates')




@app.route("/")
def index():
    return render_template("index.html")


@app.route("/charts")
def charts():
    return render_template("charts.html")


@app.route("/tables")
def tables():
    return render_template("tables.html")


@app.route("/products_create/")
def create_product():
    return render_template("add_product.html")


@app.route("/categories/create")
def create_category():
    return render_template("add_category.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

