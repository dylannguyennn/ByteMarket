from flask import Flask, render_template, redirect, url_for, flash, jsonify, request
import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql.expression import func
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_migrate import Migrate
from forms import RegistrationForm, LoginForm, ProductForm
from models import db, User, Product, CartItem
from werkzeug.utils import secure_filename
import stripe
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Stripe configuration
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
STRIPE_PUBLISHABLE_KEY = os.getenv("STRIPE_PUBLISHABLE_KEY")

# Initialize extensions
db.init_app(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create sample data if needed
def create_sample_products():
    if Product.query.first():
        return
    sample = Product(
        product_name="Sample",
        description="Sample Product",
        price=9.99,
        image_path="img/sample.png",
        category="demo",
        user_id=1
    )
    db.session.add(sample)
    db.session.commit()

with app.app_context():
    db.create_all()
    create_sample_products()

@app.route("/")
def home():
    products = Product.query.order_by(func.random()).limit(6).all()
    return render_template("index.html", products=products)

# Auth Routes
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already registered.", "danger")
            return redirect(url_for("login"))
        hashed = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        flash("Account created! Log in now.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash("Logged in!", "success")
            return redirect(url_for("home"))
        flash("Login failed.", "danger")
    return render_template("login.html", form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

@app.route("/account")
@login_required
def account():
    return render_template("account.html")

@app.route("/edit_account", methods=["GET", "POST"])
@login_required
def edit_account():
    form = RegistrationForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            current_user.password_hash = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        db.session.commit()
        flash("Account updated.", "success")
        return redirect(url_for("account"))
    form.username.data = current_user.username
    form.email.data = current_user.email
    return render_template("edit_account.html", form=form)

@app.route("/upload_product", methods=["GET", "POST"])
@login_required
def upload_product():
    if current_user.role not in ['seller', 'admin']:
        flash("No permission to upload.", "danger")
        return redirect(url_for("account"))
    form = ProductForm()
    if form.validate_on_submit():
        image = form.image.data
        filename = secure_filename(image.filename)
        folder = os.path.join(app.static_folder, 'product_images')
        os.makedirs(folder, exist_ok=True)
        image.save(os.path.join(folder, filename))
        path = os.path.join('product_images', filename)
        product = Product(
            product_name=form.product_name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            image_path=path,
            user_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash("Product uploaded!", "success")
        return redirect(url_for("account"))
    return render_template("upload_product.html", form=form)

@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product.html", product=product)

@app.route("/cart")
@login_required
def cart():
    return render_template("cart.html")

@app.route("/api/cart", methods=["GET"])
@login_required
def get_cart():
    items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart = [{
        "id": item.id,
        "product_id": item.product_id,
        "name": item.product.product_name,
        "price": item.product.price,
        "quantity": item.quantity,
        "total": item.product.price * item.quantity,
        "image_url": "/static/" + item.product.image_path
    } for item in items]
    return jsonify(success=True, cart_items=cart)

@app.route("/api/cart/add", methods=["POST"])
@login_required
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)
    item = CartItem.query.filter_by(user_id=current_user.id, product_id=product_id).first()
    if item:
        item.quantity += quantity
    else:
        item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(item)
    db.session.commit()
    return jsonify(success=True)

@app.route("/api/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart(item_id):
    data = request.get_json()
    qty = data.get("quantity", 1)
    if qty < 1:
        return jsonify(success=False, message="Minimum quantity is 1"), 400
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify(success=False), 404
    item.quantity = qty
    db.session.commit()
    return jsonify(success=True)

@app.route("/api/cart/remove/<int:item_id>", methods=["DELETE"])
@login_required
def remove_cart(item_id):
    item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first()
    if not item:
        return jsonify(success=False), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify(success=True)

# --- Stripe Payment Routes ---

@app.route("/payment")
@login_required
def payment():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.product.price * item.quantity for item in cart_items)
    return render_template("payment.html", cart_items=cart_items, total=total, stripe_key=STRIPE_PUBLISHABLE_KEY)

@app.route("/create-checkout-session", methods=["POST"])
@login_required
def create_checkout_session():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        flash("Your cart is empty.", "danger")
        return redirect(url_for("cart"))

    line_items = [{
        "price_data": {
            "currency": "usd",
            "product_data": {"name": item.product.product_name},
            "unit_amount": int(item.product.price * 100),
        },
        "quantity": item.quantity,
    } for item in cart_items]

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=url_for('thank_you', _external=True),
            cancel_url=url_for('payment', _external=True),
        )
        return redirect(session.url, code=303)
    except stripe.error.AuthenticationError:
        flash("Stripe authentication failed. Check API key.", "danger")
        return redirect(url_for("payment"))

@app.route("/thank_you")
@login_required
def thank_you():
    # Optionally clear cart after Stripe webhook success
    CartItem.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    return render_template("thank_you.html")

# --- Run the App ---
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')