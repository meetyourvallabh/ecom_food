from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    redirect,
    session,
    jsonify,
)
from database import mongo
import datetime
from random import randint
import bcrypt
from functools import wraps
from flask_cors import CORS
from collections import Counter


app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/og_tech"

mongo.init_app(app)  # Mongo
CORS(app)


from admin import admin

app.register_blueprint(admin.app, url_prefix="/admin")


# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "logged_in" in session:
            return f(*args, **kwargs)
        else:
            flash("Please Login First", "secondary")
            return redirect(url_for("login"))

    return wrap


@app.route("/")
def index():
    products = mongo.db.products.find()
    return render_template("index.html",products = products)


@app.route("/login/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form["password"]
        found_user = mongo.db.users.find_one(
            {
                "$or": [
                    {"email": request.form["user_id"]},
                    {"user_id": request.form["user_id"]},
                ]
            }
        )
        if bcrypt.checkpw(password.encode("utf-8"), found_user["password"]):
            session["fname"] = found_user["fname"]
            session["lname"] = found_user["lname"]
            session["email"] = found_user["email"]
            session["user_id"] = found_user["user_id"]
            session["logged_in"] = True

            if found_user["type"] == "admin":
                return redirect(url_for("admin.dashboard"))
            flash("Successfull Login", "success")
            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/signup/", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_id = (
            request.form["fname"][:1]
            + request.form["lname"][:2]
            + str(randint(1111, 9999))
        )
        passw = request.form["password"]
        hashpass = bcrypt.hashpw(passw.encode("utf-8"), bcrypt.gensalt())
        users = mongo.db.users
        done = users.insert_one(
            {
                "user_id": user_id,
                "fname": request.form["fname"],
                "lname": request.form["lname"],
                "password": hashpass,
                "email": request.form["email"],
                "phone": request.form["phone"],
                "created_at": datetime.datetime.now(),
                "type": "admin",
            }
        )
        if done:
            flash("Successfully created account", "success")
            return redirect(url_for("login"))
        else:
            flash("Somethign went wrong", "danger")
    return render_template("signup.html")


@app.route("/shop_details/")
def shop_details():
    return render_template("shop-details.html")


@app.route("/shopping_cart/")
def shopping_cart():

    
    
    cart = []
    if 'cart' in session:
        products = session['cart']['products']
        products_collection = mongo.db.products
        for prod,quantity in products.items():
            product = products_collection.find_one({'product_id':prod})
            product_dict = {
                'photo':product['photo'],
                'price':int(product['price']),
                'name':product['name'],
                'quantity': quantity,
                'product_total': int(product['price']) * int(quantity)
            }
            cart.append(product_dict)

        print(session['cart'])
    return render_template("shopping-cart.html",cart = cart)


@app.route("/checkout/")
def checkout():
    return render_template("checkout.html")


@app.route("/blog_details/")
def blog_details():
    return render_template("blog-details.html")


@app.route("/add_to_cart/<product_id>", methods=["POST"])
def add_to_cart(product_id):
    product = mongo.db.products.find_one({'product_id':product_id})
    if 'cart' in session:
        print(session['cart'])
        product_dict = session['cart']['products']
        if product_id in product_dict:
            #add number
            product_dict[product_id] += 1
        else:
            #add key value
            product_dict[product_id] = 1
        total_price = int(session['cart']['cart_total'])
        total_price += int(product['price']) 
        session['cart'] = {
            'products':product_dict,
            'cart_total': total_price
        }    
    else:
        session['cart']={
            'products':{
                product_id:1
            },
            'cart_total': int(product['price'])
        }
    print(session['cart'])
    return jsonify({
        "result": "product added " + product_id,
        "total_products": len(session['cart']['products']),
        "cart_total": session['cart']['cart_total']
        })

@app.route('/cart/update_quantity/<product_id>', methods=['POST'])
def update_product_quantity(product_id):
    if 'cart' in session:
        #print(request.body)
        pass
    return jsonify({"result":"updated"})


@app.route("/logout/")
@is_logged_in
def logout():
    if "logged_in" in session:
        session.clear()
        flash("Successfully logged out", "success")
        return redirect(url_for("login"))
    else:
        flash("You are not Logged in", "secondary")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.secret_key = "skapa"
    app.run(debug=True)
