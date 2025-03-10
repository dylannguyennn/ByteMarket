from flask import Flask, render_template, redirect, url_for, flash, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm  # Import LoginForm
from models import db, User, Product, CartItem

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)  # Initialize db AFTER creating app
bcrypt = Bcrypt(app)  # Initialize Bcrypt
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect unauthorized users to login

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Fetch user by ID

# Route: Main Page
@app.route("/")
def home():
    if current_user.is_authenticated:
        return render_template("index.html")  # Load the signed-in homepage
    return render_template("index.html")  # Load the guest homepage

# Route: Register
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()  # Check if email exists
        if existing_user:
            flash("This email is already registered. Please log in.", "danger")
            return redirect(url_for("login"))  # Redirect to login page if email exists

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(username=form.username.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("login"))  # Redirect to login page

    return render_template("register.html", form=form)

# Route: Login
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)  # Logs in the user
            flash("You have successfully logged in!", "success")
            return redirect(url_for("home"))  # Redirect to home page
        else:
            flash("Login unsuccessful. Check email and password.", "danger")
    return render_template("login.html", form=form)

# Route: Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


# Route: Account Page
@app.route("/account")
@login_required  # Ensures only logged-in users can access the account page
def account():
    return render_template("account.html")  # Ensure account.html exists in /templates

# Route: Edit Account
@app.route("/edit_account", methods=["GET", "POST"])
@login_required
def edit_account():
    form = RegistrationForm()  # Reusing the registration form for now
    if form.validate_on_submit():
        # Update user details if they enter new ones
        current_user.username = form.username.data
        current_user.email = form.email.data
        if form.password.data:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
            current_user.password_hash = hashed_password
        db.session.commit()
        flash("Your account has been updated!", "success")
        return redirect(url_for("account"))
    
    # Pre-fill form fields with current user data
    form.username.data = current_user.username
    form.email.data = current_user.email

    return render_template("edit_account.html", form=form)

# Route: Cart Page
@app.route("/cart")
@login_required  # Ensures only logged-in users can access the cart
def cart():
    return render_template("cart.html")  # Ensure cart.html exists in /templates

# Route: Product Page
@app.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product.html", product=product)

# API to add product to cart
@app.route("/api/cart/add", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    product_id = data.get("product_id")
    quantity = data.get("quantity", 1)

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"success": False, "message": "Product not found"}), 404
    
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first()

    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, product_id=product_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({"success": True, "message": "Item added to cart"})

# API to get cart items (i.e when on cart page)
@app.route("/api/cart", methods=["GET"])
@login_required
def get_cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    cart_data = []

    for item in cart_items:
        cart_data.append({
            "id": item.id,
            "product_id": item.product_id,
            "name": item.product.name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total": item.product.price * item.quantity,
            "image_url": item.product.image_url
        })
    
    return jsonify({"success": True, "cart_items": cart_data})

if __name__ == "__main__":

    app.run(debug=True)