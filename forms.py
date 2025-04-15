from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired # Added for file uploads
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FloatField # Added TextAreaField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length

# Registration Form
class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Register")

# Login Form
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

# Product Upload Form
class ProductForm(FlaskForm):
    product_name = StringField("Product Name", validators=[DataRequired(), Length(max=200)])
    description = TextAreaField("Description", validators=[DataRequired()])
    price = FloatField("Price", validators=[DataRequired()])
    category = StringField("Category", validators=[DataRequired(), Length(max=255)])
    image = FileField("Product Image", validators=[FileRequired(), FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    submit = SubmitField("Upload Product")