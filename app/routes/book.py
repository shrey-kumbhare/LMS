"""
A module that Imports book using the Frappe API, adds book to the library database, allows Librarian
to search for books, updates book details, deletes book details, and view all books
"""
from flask import Flask, Blueprint, flash, redirect, url_for, render_template, request
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length, NumberRange
from app.models import Book, db
import requests

app = Flask(__name__)

# Create the books blueprint
bp = Blueprint('book', __name__)

class ImportBooksForm(FlaskForm):
    """
    A class that creates a form object to import books
    """
    search = StringField('Search by Title or Author', validators=[InputRequired(), Length(max=255)])
    submit = SubmitField('Search Frappe Library')

class AddBookForm(FlaskForm):
    """
    A class that creates a form object to add books
    """
    author = StringField('Author', validators=[InputRequired(), Length(max=255)])
    title = StringField('Title', validators=[InputRequired(), Length(max=255)])
    publisher = StringField('Publisher', validators=[InputRequired(), Length(max=255)])
    isbn = StringField('ISBN', validators=[InputRequired(), Length(max=20)])
    quantity = IntegerField('Quantity', validators=[InputRequired(), NumberRange(min=1, max=30)])
    submit = SubmitField('Add Book')

class SearchBooksForm(FlaskForm):
    """
    A class that creates a form object to search for books
    """
    search = StringField('Search by Title or Author', validators=[InputRequired(), Length(max=255)])
    submit = SubmitField('Delete')
    submit = SubmitField('Update')

class DeleteBooksForm(FlaskForm):
    """
    A class that creates a form object to delete books
    """
    author = StringField('Author', validators=[InputRequired(), Length(max=255)])
    title = StringField('Title', validators=[InputRequired(), Length(max=255)])
    publisher = StringField('Publisher', validators=[InputRequired(), Length(max=255)])
    isbn = StringField('ISBN', validators=[InputRequired(), Length(max=20)])
    quantity= IntegerField('Quantity', validators=[InputRequired(), NumberRange(min=1, max=30)])
    submit = SubmitField('Delete')

class UpdateBookForm(FlaskForm):
    """
    Class that creates a form object to update book details
    """
    author = StringField('Author', validators=[InputRequired(), Length(max=255)])
    title = StringField('Title', validators=[InputRequired(), Length(max=255)])
    publisher = StringField('Publisher', validators=[InputRequired(), Length(max=255)])
    isbn = StringField('ISBN', validators=[InputRequired(), Length(max=20)])
    submit = SubmitField('Update')

# A route for importing books
@bp.route('/import-books', methods=['GET', 'POST'])
def import_books():
    """
    A route that imports books using the Frappe API
    """
    form = ImportBooksForm()

    if request.method == 'POST' and form.validate_on_submit():
        search_query = form.search.data

        # Define the API URL
        frappe_api_url = "https://frappe.io/api/method/frappe-library"

        # Prepare parameters for the API request
        params = {
            'title': search_query,  # Search by title
            'authors': search_query,  # Search by authors
            'isbn': 1,  
            'publisher': 1,  
        }
        try:
            # Fetch data from the API
            response = requests.get(frappe_api_url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()["message"]

                # Filter the API results to include only books with matching titles or authors
                matching_books = [book for book in data if
                                    search_query.lower() in book["title"].lower() or
                                    search_query.lower() in book["authors"].lower()]
                if not matching_books:
                    flash("No matching books found.", "warning")
                return render_template('book/import_books.html', search_results=matching_books, form=form)
            else:
                print("Request failed with timeout:", response.status_code)
        except requests.Timeout:
            print("The request timed out")
    return render_template('book/import_books.html', form=form)

# A route for adding books to library
@bp.route('/add-book', methods=['POST', 'GET'])
def add_book():
    """
    A route that adds books to the database
    """
    # Retrieve book details from the form 
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        isbn = request.form.get('isbn')
        publisher = request.form.get('publisher')
    else:
        # Retrieve book details from url parameters
        title = request.args.get('title')
        author = request.args.get('author')
        isbn = request.args.get('isbn')
        publisher = request.args.get('publisher')

    # Create the form and populate it with the book details
    form = AddBookForm(title=title, author=author, isbn=isbn, publisher=publisher)

    if request.method == 'POST' and form.validate_on_submit():
        # Handle the form submission (add the books to the database)
        quantity = form.quantity.data
        # Check if the ISBN exists in the table
        existing_book = Book.query.filter(Book.isbn==isbn).first()
        if existing_book:
            # Increment the db quantity by the librarian's input
            existing_book.Quantity+=quantity
        else:
            new_book = Book(title=title, author=author, isbn=isbn, publisher=publisher, Quantity=quantity)
            db.session.add(new_book)
            
        db.session.commit()
        flash(f'Successfully added {quantity} books to the library!', 'success')
        return redirect(url_for('book.all_books'))

    return render_template('book/add_book.html', form=form)

# Route for deleting books
@bp.route('/delete-book', methods=['GET', 'POST'])
def delete_book():
    """
    A route that deletes books in the database
    """
    # Retrieve book details from query parameters
    title = request.args.get('title')
    author = request.args.get('author')
    isbn = request.args.get('isbn')
    publisher = request.args.get('publisher')

    # Query the database for the book with the specified ISBN
    book_to_delete = Book.query.filter_by(isbn=isbn).first()

    if book_to_delete:
        # Create the form and populate it with the book details
        form = DeleteBooksForm(title=title, author=author, isbn=isbn, publisher=publisher)

        if request.method == 'POST' and form.validate_on_submit():
            quantity_to_delete = form.quantity.data
            existing_quantity = book_to_delete.Quantity

            if quantity_to_delete <= existing_quantity:
                # Update the quantity in the database
                book_to_delete.Quantity -= quantity_to_delete

                db.session.commit()
                flash(f'Successfully deleted {quantity_to_delete} copy(ies) of {book_to_delete.title} from the library!', 'success')
                return redirect(url_for('book.search_books'))
            
            flash('Quantity to delete is greater than existing quantity.', 'warning')
    else:
        flash('Book not found', 'danger')

    return render_template('book/delete_book.html', form=form, book=book_to_delete)

@bp.route('/update-book/<int:book_id>', methods=['GET', 'POST'])
def update_book(book_id):
    """
    A route that updates the properties of a particular book in the database
    """
    book_to_update = Book.query.get(book_id)
    form = UpdateBookForm()

    if book_to_update:
        if request.method == 'GET':
            # Pre-fill the form with book data
            form.title.data = book_to_update.title
            form.author.data = book_to_update.author
            form.isbn.data = book_to_update.isbn
            form.publisher.data = book_to_update.publisher

        if form.validate_on_submit() and request.method == 'POST':
            # Update the book details based on the form data
            book_to_update.title = form.title.data
            book_to_update.author = form.author.data
            book_to_update.isbn = form.isbn.data
            book_to_update.publisher = form.publisher.data
            db.session.commit()
            flash(f"{book_to_update.title} has been successfully updated", "success")
            return redirect(url_for('book.search_books'))
    return render_template('book/update_book.html', form=form, book_to_update=book_to_update, book_id=book_id)

@bp.route('/search-books', methods=['POST', 'GET'])
def search_books():
    """
    A route that allows the librarian to search for any book using title or author
    """
    form = SearchBooksForm()

    book_list = []
    if request.method == 'POST':
        search_query = form.search.data
        # Query the database by author or title
        book_list = Book.query.filter(Book.title.like(f'%{search_query}%') | Book.author.like(f'%{search_query}%')).all()

        if not book_list:
            flash("No matching book copies found in the library")
            return render_template("book/search_books.html", form=form)

    return render_template("book/search_books.html", form=form, book_list=book_list)

@bp.route('/all-books', methods=['GET'])
def all_books():
    """
    A route that displays all books in the library
    """
    # Query the database for all books
    library_books = Book.query.all()
    return render_template('book/all_books.html', library_books=library_books)
