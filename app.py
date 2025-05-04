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
    
    products = [
        Product(
            product_name="Cat Phone Icons",
            description="Give your device a fresh look with our awesome icon and wallpaper set for iOS, iPadOS, and Android! This digital download includes 126 stunning icons covering a range of popular apps that can be used to customize any app on your device. You'll get high-resolution PNG files designed for both mobile phones and tablets, so your screens will look fantastic no matter what device you’re using!",
            price=9.99,
            image_path="product_images/cat_icons.png",
            category="art",
            user_id=1
        ),
        Product(
            product_name="Cleaning Schedule Planner",
            description="This cleaning planner helps you plan and manage your household cleaning all year round! Use this schedule to keep track of all your hard to remember chores to make sure your home stays clean and organized and check off tasks as you do them.",
            price=4.99,
            image_path="product_images/cleaning_planner.png",
            category="pdfs",
            user_id=1
        ),
        Product(
            product_name="Cracking the Coding Interview e-Book",
            description="Cracking the Coding Interview is here to help you through this process, teaching you what you need to know and enabling you to perform at your very best. I've coached and interviewed hundreds of software engineers. The result is this book.Learn how to uncover the hints and hidden details in a question, discover how to break down a problem into manageable chunks, develop techniques to unstick yourself when stuck, learn (or re-learn) core computer science concepts, and practice on 189 interview questions and solutions.",
            price=29.99,
            image_path="product_images/ebook.png",
            category="ebooks",
            user_id=1
        ),
        Product(
            product_name="Art Sample #1",
            description="This is a sample art piece that showcases the artist's unique style and creativity. It is a digital download that can be printed and framed to add a touch of elegance to any room.",
            price=9.99,
            image_path="product_images/art1.png",
            category="art",
            user_id=1
        ),
        Product(
            product_name="Amazon Gift Card",
            description="This Amazon gift card is a prepaid card that can be used to purchase products and services on Amazon.com. It is a convenient way to shop online without the need for a credit card or bank account.",
            price=50.00,
            image_path="product_images/amazon_gc.png",
            category="egiftcards",
            user_id=1
        ),
        Product(
            product_name="Target Gift Card",
            description="This Target gift card is a prepaid card that can be used to purchase products and services at Target stores or on their website. It is a convenient way to shop without the need for cash or credit cards.",
            price=50.00,
            image_path="product_images/target_gc.png",
            category="egiftcards",
            user_id=1
        ),
        Product(
            product_name="Visa Gift Card",
            description="This Visa gift card is a prepaid card that can be used to make purchases anywhere Visa is accepted. It is a convenient way to shop without the need for cash or credit cards.",
            price=50.00,
            image_path="product_images/visa_gc.png",
            category="egiftcards",
            user_id=1
        ),
        Product(
            product_name="Prelude by Johann Sebastian Bach",
            description="This is a Prelude by Johann Sebastian Bach, a famous composer from the Baroque period. It is a beautiful piece of music that is often played on the piano.",
            price=1.99,
            image_path="product_images/bach.svg",
            category="music",
            user_id=1
        ),
        Product(
            product_name="Sonata by Ludwig van Beethoven",
            description="This is a Sonata by Ludwig van Beethoven, a famous composer from the Classical period. It is a beautiful piece of music that is often played on the piano.",
            price=1.99,
            image_path="product_images/beet.svg",
            category="music",
            user_id=1
        ),
        Product(
            product_name="Concerto by Wolfgang Amadeus Mozart",
            description="This is a Concerto by Wolfgang Amadeus Mozart, a famous composer from the Classical period. It is a beautiful piece of music that is often played on the piano.",
            price=1.99,
            image_path="product_images/mozart.svg",
            category="music",
            user_id=1
        ),
        Product(
            product_name="Biology Study Guide",
            description="This is a Biology Study Guide, a comprehensive guide to the subject of biology. It covers all the major topics in biology and provides detailed explanations and examples.",
            price=5.99,
            image_path="product_images/biology.png",
            category="pdfs",
            user_id=1
        ),
        Product(
            product_name="Calculus Study Guide",
            description="This is a Calculus Study Guide, a comprehensive guide to the subject of calculus. It covers all the major topics in calculus and provides detailed explanations and examples.",
            price=6.99,
            image_path="product_images/calculus.png",
            category="pdfs",
            user_id=1
        ),
        Product(
            product_name="Of Mice and Men",
            description="Of Mice and Men is a novella written by John Steinbeck, published in 1937. It tells the story of two displaced migrant ranch workers who try to make a living during the Great Depression in California.",
            price=12.99,
            image_path="product_images/mice.svg",
            category="ebooks",
            user_id=1
        ),
        Product(
            product_name="The Art of War",
            description="The Art of War is an ancient Chinese military treatise attributed to Sun Tzu, a high-ranking military general, strategist, and tactician. It is composed of 13 chapters, each dedicated to a different aspect of warfare.",
            price=13.99,
            image_path="product_images/war.svg",
            category="ebooks",
            user_id=1
        ),
        Product(
            product_name="Adventures of Huckleberry Finn",
            description="Adventures of Huckleberry Finn is a novel written by Mark Twain, published in 1884. It is a sequel to The Adventures of Tom Sawyer and tells the story",
            price=12.99,
            image_path="product_images/huck.svg",
            category="ebooks",
            user_id=1
        )
    ]

    for product in products:
        db.session.add(product)

    db.session.commit()

with app.app_context():
    db.create_all()
    create_sample_products()

@app.route("/")
def home():
    products = Product.query.order_by(func.random()).limit(6).all()
    return render_template("index.html", products=products)

# Route: Searching
@app.route("/api/search", methods=["GET"])
def search_products():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"success": False, "message": "No search query provided"}), 400

    products = Product.query.filter(Product.product_name.icontains(query)).all()

    results = []
    for product in products:
        results.append({
            "id": product.id,
            "name": product.product_name,
            "description": product.description[:100] + "..." if len(product.description) > 100 else product.description,
            "price": product.price,
            "image_path": product.image_path
        })

    return jsonify({"success": True, "results": results, "count": len(results)})

@app.route("/category/<category_name>")
def category(category_name):
    products = Product.query.filter_by(category=category_name).all()
    return render_template("_products.html", products=products)

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