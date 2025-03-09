from flask import Flask, render_template, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm  # Import LoginForm
from models import db, User

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
# Route URL is temporary; needs to be modified to include product ID
@app.route("/product")
def product():
    return render_template("product.html")

if __name__ == "__main__":

    app.run(debug=True)