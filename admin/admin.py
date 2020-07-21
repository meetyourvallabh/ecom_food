from flask import Blueprint, render_template, jsonify, url_for, redirect, request, flash
import datetime, string
from database import mongo
from random import *
import os
from PIL import Image
from werkzeug.utils import secure_filename

basedir_admin = (os.path.abspath(os.path.dirname(__file__))).rsplit("/", 1)
#basedir_admin = (os.path.abspath(os.path.dirname(__file__))).rsplit("\\", 1)
print(basedir_admin)
admin_upload = basedir_admin[0]


print(admin_upload)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app = Blueprint("admin", __name__, template_folder="templates")


@app.route("/")
def dashboard():
    return render_template("dashboard.html")


@app.route("/charts")
def charts():
    return render_template("charts.html")


@app.route("/tables")
def tables():
    return render_template("tables.html")


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/products/create/", methods=["POST", "GET"])
def create_product():
    if request.method == "POST":
        product_name = request.form["name"]
        product_description = request.form["description"]
        product_price = request.form["price"]
        product_category = request.form["category"]
        product_stock = request.form["stock"]
        product_id = product_name[:2] + str(randint(111, 999))

        if "photo" not in request.files:
            flash("No file part")
            return redirect(request.url)

        product_photo = request.files["photo"]

        if allowed_file(product_photo.filename):
            path = os.path.abspath(
                admin_upload + "/static/images/products/" + product_id
            )
            if not os.path.exists(path):
                os.makedirs(path)
                print("directory created")
            file_name = secure_filename(product_photo.filename)

            f = os.path.join(path, file_name)
            product_photo.save(f)

        done = mongo.db.products.insert_one(
            {
                "product_id": product_id,
                "photo": "/images/products/" + product_id + "/" + file_name,
                "name": product_name,
                "description": product_description,
                "category": product_category,
                "price": product_price,
                "stock": product_stock,
                "sold": 0,
            }
        )
        if done:
            flash('"' + product_name + '" created successfully!', "success")
            return redirect(url_for("admin.products"))
        else:
            flash('"' + product_name + '" could not be created', "danger")
    elif request.method == "GET":
        all_categories = mongo.db.categories.find()
    return render_template("add_product.html", all_categories=all_categories)


@app.route("/categories/create", methods=["POST", "GET"])
def create_category():
    if request.method == "POST":
        category_name = request.form["name"]
        category_id = category_name[:2] + str(randint(111, 999))

        done = mongo.db.categories.insert_one(
            {"category_id": category_id, "name": category_name,}
        )

        if done:
            flash('"' + category_name + '" created successfully!', "success")
            return redirect(url_for("admin.categories"))
        else:
            flash('"' + category_name + '" could not be created', "danger")
            return redirect(url_for("admin.create_category"))

    return render_template("add_category.html")

@app.route("/pincodes/create", methods=["POST", "GET"])
def create_pincode():
    if request.method == "POST":
        pincode_code = request.form["pincode"]
        pincode_area = request.form["area"]
        pincode_city = request.form["city"]

        done = mongo.db.pincodes.insert_one(
            {"pincode": pincode_code, "area": pincode_area, "city": pincode_city}
        )

        if done:
            flash('"' + pincode_code + '" created successfully!', "success")
            return redirect(url_for("admin.pincodes"))
        else:
            flash('"' + pincode_code + '" could not be created', "danger")
            return redirect(url_for("admin.create_pincode"))

    return render_template("add_pincode.html")


@app.route("/products")
def products():
    all_products = mongo.db.products.find()
    return render_template("all_products.html", all_products=all_products)


@app.route("/categories")
def categories():
    all_categories = mongo.db.categories.find()
    return render_template("all_categories.html", all_categories=all_categories)


@app.route("/pincodes")
def pincodes():
    all_pincodes = mongo.db.pincodes.find()
    return render_template("all_pincodes.html", all_pincodes=all_pincodes)


@app.route("/products/update/<product_id>", methods=["GET", "POST"])
def update_product(product_id):
    if request.method == "POST":
        new_name = request.form["name"]
        new_description = request.form["description"]
        new_price = request.form["price"]
        new_category = request.form["category"]
        new_stock = request.form["stock"]

        if "photo" not in request.files:
            flash("No file part")
            return redirect(request.url)

        product_photo = request.files["photo"]

        if allowed_file(product_photo.filename):
            path = os.path.abspath(
                admin_upload + "/static/images/products/" + product_id
            )
            if not os.path.exists(path):
                os.makedirs(path)
                print("directory created")
            file_name = secure_filename(product_photo.filename)

            f = os.path.join(path, file_name)
            product_photo.save(f)

        done = mongo.db.categories.update_one(
            {"product_id": product_id},
            {
                "$set": {
                    "name": new_name,
                    "description": new_description,
                    "price": new_price,
                    "category": new_category,
                    "stock": new_stock,
                }
            },
        )
        if done:
            flash("Product successfully updated!", "success")
            return redirect(url_for("admin.products"))
        else:
            flash("Couldn't update product", "danger")
            return redirect(url_for("admin.update_product", product_id=product_id))
    elif request.method == "GET":
        found_product = mongo.db.products.find_one({"product_id": product_id})
    return render_template("update_product.html", found_product=found_product)


@app.route("/categories/update/<category_id>", methods=["GET", "POST"])
def update_category(category_id):
    if request.method == "POST":
        new_name = request.form["name"]
        done = mongo.db.categories.update_one(
            {"category_id": category_id}, {"$set": {"name": new_name,}}
        )
        if done:
            flash("Category successfully updated!", "success")
            return redirect(url_for("admin.categories"))
        else:
            flash("Couldn't update category", "danger")
            return redirect(url_for("admin.update_category", category_id=category_id))
    found_category = mongo.db.categories.find_one({"category_id": category_id})
    return render_template("update_category.html", found_category=found_category)

@app.route("/pincodes/update/<pincode>", methods=["GET", "POST"])
def update_pincode(pincode):
    if request.method == "POST":
        new_pincode = request.form["pincode"]
        new_area = request.form["area"]
        new_city = request.form["city"]
        done = mongo.db.pincodes.update_one(
            {"pincode": pincode}, {"$set": {"pincode": new_pincode, "area": new_area, "city": new_city}}
        )
        if done:
            flash("Pincode successfully updated!", "success")
            return redirect(url_for("admin.pincodes"))
        else:
            flash("Couldn't update pincode", "danger")
            return redirect(url_for("admin.update_pincode", pincode=pincode))
    found_pincode = mongo.db.pincodes.find_one({"pincode": pincode})
    return render_template("update_pincode.html", found_pincode=found_pincode)


@app.route("/products/delete/<product_id>", methods=["GET", "POST"])
def delete_product(product_id):
    done = mongo.db.products.delete_one({"product_id": product_id})
    if done:
        flash("Product successfully deleted!", "success")
        return redirect(url_for("admin.products"))
    else:
        flash("Product couldn't be deleted!", "danger")
        return redirect(url_for("admin.products"))

@app.route("/pincodes/delete/<pincode>", methods=["GET", "POST"])
def delete_pincode(pincode):
    done = mongo.db.pincodes.delete_one({"pincode": pincode})
    if done:
        flash("Pincode successfully deleted!", "success")
        return redirect(url_for("admin.pincodes"))
    else:
        flash("Pincode couldn't be deleted!", "danger")
        return redirect(url_for("admin.pincodes"))


@app.route("/categories/delete/<category_id>", methods=["GET", "POST"])
def delete_category(category_id):
    done = mongo.db.categories.delete_one({"category_id": category_id})
    if done:
        flash("Category successfully deleted!", "success")
        return redirect(url_for("admin.categories"))
    else:
        flash("Category couldn't be deleted!", "danger")
        return redirect(url_for("admin.categories"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)

