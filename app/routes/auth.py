"""
A module that contains the registration, login, and home page
"""

from flask import Flask, current_app as app, render_template, request, Blueprint, flash, redirect, url_for
from flask_login import logout_user, login_user, login_required
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError
from app.models import Member, Book, Transaction, db

# Configure Bootstrap
app = Flask(__name__)
Bootstrap(app)

# Create the auth blueprint
bp = Blueprint('auth', __name__)


class LoginForm(FlaskForm):
    """
    A class that creates a login form object
    """
    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=15)])
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    """
    A class the creates a registration form object
    """

    username = StringField('Username', validators=[InputRequired(), Length(min=4, max=15)])
    fullname = StringField('Full Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=15)])
    confirm_password = PasswordField('Confirm Password', validators=[InputRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        Custom validator to check if the username is already taken.
        """
        existing_user = Member.query.filter_by(username=username.data).first()
        if existing_user:
            raise ValidationError('Username is already taken. Please choose another username.')

    def validate_email(self, email):
        """
        Custom validator to check if the email is already registered.
        """
        existing_email = Member.query.filter_by(email=email.data).first()
        if existing_email:
            raise ValidationError('Email address is already registered. Please use a different email address.')


# Login  route
@bp.route('/')
@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route
    """
    form = LoginForm()
    if form.validate_on_submit():
        # Retrieve the user by username from the database
        user = Member.query.filter_by(username=form.username.data).first()

        if user and user.verify_password(form.password.data):  
            login_user(user)  # Log in the user
            flash('Login successful', 'success')
            return redirect(url_for('auth.home')) 
        else:
            flash('Invalid username or password', 'danger')

    return render_template('auth/login.html', form=form)

# Home route
@bp.route('/home')
@login_required
def home():
    """
    Homepage
    """
    # Query for total books, members, and transactions
    total_books = Book.query.count()
    total_members = Member.query.count()
    total_transactions = Transaction.query.count()
    ongoing_issues = Transaction.query.filter(Transaction.return_date==None).count()


    return render_template('auth/home.html',  ongoing_issues=ongoing_issues, total_books=total_books,  total_members=total_members,  total_transactions= total_transactions )

# Registration route
@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route
    """
    form = RegistrationForm()
    if form.validate_on_submit():
        new_member = Member(username=form.username.data, fullname=form.fullname.data, email=form.email.data)
        new_member.create_password(form.password.data)
        db.session.add(new_member)
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('auth.login'))  # Redirect to the login page after successful registration

    if request.method == 'GET':
        return render_template('auth/register.html', form=form)
    
    return render_template('auth/register.html', form=form)

@bp.route('/logout')
@login_required  
def logout():
    """
    Logout route
    """
    logout_user() 
    flash('Logged out successfully', 'success')
    return redirect(url_for('auth.login'))
