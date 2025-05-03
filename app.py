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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'  # Change in production
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # SQLite database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Function to populate database with sample products
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
    print("Sample products created...")
    
db.init_app(app)  # Initialize db AFTER creating app
bcrypt = Bcrypt(app)  # Initialize Bcrypt
migrate = Migrate(app, db) # Initialize Flask-Migrate
login_manager = LoginManager(app)
login_manager.login_view = "login"  # Redirect unauthorized users to login
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

with app.app_context():
    db.create_all()
    create_sample_products()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # Fetch user by ID

# Route: Main Page
@app.route("/")
def home():
    # Randomly select (6) featured products
    products = Product.query.order_by(func.random()).limit(6).all()
    if current_user.is_authenticated:
        return render_template("index.html", products=products)  # Load the signed-in homepage
    else:
        return render_template("index.html", products=products)  # Load the guest homepage

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

# Route: Category Page
@app.route("/category/<category_name>")
def category(category_name):
    products = Product.query.filter_by(category=category_name).all()
    return render_template("_products.html", products=products)

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

# Route: Upload Product Page 
@app.route("/upload_product", methods=["GET", "POST"])
@login_required
def upload_product():
    if current_user.role not in ['seller', 'admin']:
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('account'))  
    
    form = ProductForm() 

    if form.validate_on_submit(): # Process form data on POST if valid
        image_file = form.image.data
        filename = secure_filename(image_file.filename)

        # Define the path relative to the static folder
        image_folder = os.path.join(app.static_folder, 'product_images')

        # Create the directory if it doesn't exist
        os.makedirs(image_folder, exist_ok=True)
        image_path_full = os.path.join(image_folder, filename)
        image_file.save(image_path_full)
        
        image_path_db = os.path.join('product_images', filename)

        new_product = Product(
            product_name=form.product_name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data, 
            image_path=image_path_db, 
            user_id=current_user.id 
        )

        db.session.add(new_product)
        db.session.commit()

        flash("Product uploaded successfully!", "success")
        return redirect(url_for('account')) 

    # If GET request or form validation fails, render the template with the form
    return render_template("upload_product.html", form=form)

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
@login_required
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
            "name": item.product.product_name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total": item.product.price * item.quantity,
            "image_url": "/static/" + item.product.image_path,
            "image_path": item.product.image_path
        })
    
    return jsonify({"success": True, "cart_items": cart_data})

# API to update cart item quantity
@app.route("/api/cart/update/<int:item_id>", methods=["POST"])
@login_required
def update_cart_item(item_id):
    data = request.get_json()
    quantity = data.get("quantity", 1)
    
    # Ensure quantity is at least 1
    if quantity < 1:
        return jsonify({"success": False, "message": "Quantity must be at least 1"}), 400
    
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first()
    
    if not cart_item:
        return jsonify({"success": False, "message": "Item not found in cart"}), 404
    
    cart_item.quantity = quantity
    db.session.commit()
    
    return jsonify({"success": True, "message": "Cart updated successfully"})

# API to remove item from cart
@app.route("/api/cart/remove/<int:item_id>", methods=["DELETE"])
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.filter_by(
        id=item_id,
        user_id=current_user.id
    ).first()
    
    if not cart_item:
        return jsonify({"success": False, "message": "Item not found in cart"}), 404
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Item removed from cart"})

if __name__ == "__main__":

    app.run(debug=True)

# API for payment payment page
@app.route("/payment", methods=["GET"])
@login_required
def payment():
    return render_template("payment.html")

# API to process payment
@app.route("/process_payment", methods=["POST"])
@login_required
def process_payment():
    email = request.form.get("email")
    card_number = request.form.get("card_number")
    expiry_date = request.form.get("expiry_date")
    cvv = request.form.get("cvv")

    # Backend validation
    if not email or not card_number or not expiry_date or not cvv:
        flash("All fields are required.", "danger")
        return render_template("payment.html", email=email, card_number=card_number, expiry_date=expiry_date, cvv=cvv)

    if not card_number.isdigit() or len(card_number) not in [15, 16]:
        flash("Card number must be 15 or 16 digits.", "danger")
        return render_template("payment.html", email=email, card_number=card_number, expiry_date=expiry_date, cvv=cvv)

    if not expiry_date.isdigit() or len(expiry_date) != 4:
        flash("Expiry date must be 4 digits (MMYY).", "danger")
        return render_template("payment.html", email=email, card_number=card_number, expiry_date=expiry_date, cvv=cvv)

    if not cvv.isdigit() or len(cvv) != 3:
        flash("CVV must be 3 digits.", "danger")
        return render_template("payment.html", email=email, card_number=card_number, expiry_date=expiry_date, cvv=cvv)

    # Retrieve all items in the cart
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()

    # Prepare cart data for the "Thank You" page
    purchased_items = [
        {
            "name": item.product.product_name,
            "price": item.product.price,
            "quantity": item.quantity,
            "total": item.product.price * item.quantity,
        }
        for item in cart_items
    ]

    # Clear the cart
    for item in cart_items:
        db.session.delete(item)
    db.session.commit()

    # Render the "Thank You" page with purchased items
    return render_template("thank_you.html", email=email, purchased_items=purchased_items)
