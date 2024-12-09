"""
A module allows the librarian to issues ooks, return books, and view transactions

"""
from datetime import date
from flask import current_app as app, render_template, request, Blueprint, flash, redirect, url_for
from app.models import Transaction, Member, Book, db
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField, IntegerField, FloatField
from wtforms.validators import InputRequired
from sqlalchemy.exc import SQLAlchemyError

# Create the transactions blueprint

bp = Blueprint('transactions', __name__)


class IssueBookForm(FlaskForm):
    """
    A class that creates a form object for issuing books
    """
    member = SelectField('Select Member', validators=[InputRequired()], coerce=int)
    book = SelectField('Select Book', validators=[InputRequired()], coerce=int)
    submit = SubmitField('Issue Book')

class ReturnBookForm(FlaskForm):
    """
    A class that creates a form object for returning books
    """
    transaction_id = IntegerField('Transaction ID', validators=[InputRequired()])
    days_rented = IntegerField('Days rented', validators=[InputRequired ()])
    total_fee = FloatField('Total fee', validators=[InputRequired ()])
    Amount_paid = FloatField('Amount paid', validators=[InputRequired()])
    submit = SubmitField('Return Book')


# Issue Book
@bp.route('/issue-book', methods=['GET', 'POST'])
def issue_book():
    """
    A route for issuing books 
    """
    form = IssueBookForm()

    # Fill the form dropdowns with all members and books from the database
    form.member.choices = [(member.id, member.fullname) for member in Member.query.all()]
    form.book.choices = [(book.id, book.title) for book in Book.query.all()]

    if request.method == 'POST' and form.validate_on_submit():
        member_id = form.member.data
        book_id = form.book.data
                    
        # Check if the user has already borrowed a book
        existing_transaction = Transaction.query.filter_by(member_id=member_id, return_date=None).first()
        if existing_transaction:
            flash(f"{Member.query.get(member_id).fullname} has already borrowed a book", "error")
            return redirect(url_for('transactions.issue_book'))
        
        # Check if the book is available for issue
        selected_book = Book.query.get(book_id)
        if selected_book and selected_book.Quantity >= 1:
            # Fetch the per_day_fee from the Transaction table
            transaction = Transaction.query.filter_by(book_id=book_id, return_date=None).first()
            
            # Create a new transaction record with per_day_fee from the selected book
            transaction = Transaction(
                member_id=member_id,
                book_id=book_id,
                borrowed_date=date.today()
                )

            try:
                # Decrease the total available copies of the selected book by 1
                selected_book.Quantity -= 1

                # Commit the changes to the database
                db.session.add(transaction)
                db.session.commit()

                flash(f'Book: "{selected_book.title}" issued to {Member.query.get(member_id).fullname}', "success")
                return redirect(url_for('transactions.issue_book'))

            except SQLAlchemyError as exception:
                db.session.rollback()
                flash(f"An error occurred while issuing the book: {str(exception)}", "error")
        else:
            flash(f"Book '{selected_book.title}' is not available for issue", "error")

    return render_template('transaction/issue_book.html', form=form)


@bp.route('/return-book/<int:transaction_id>', methods=['GET', 'POST'])
def return_book(transaction_id):
    """
    A route for returning books 
    """
    # Fetch the transaction by ID
    transaction = Transaction.query.get(transaction_id)
    member = Member.query.get(transaction.member_id)

    if transaction:
        # Calculate the total fee based on days rented and the per-day fee
        return_date = date.today()
        borrowed_date = transaction.borrowed_date

        # Calculate the number of days rented
        days_rented = (return_date - borrowed_date).days

        # Calculate the total rent based on the number of days rented and the per-day fee
        total_fee = days_rented * 50

        if days_rented < 1:
            # Automatically charge 50 if the book is returned in less than a day
            total_fee = 50.0

        # Initialize the form with prefilled data
        form = ReturnBookForm(
            transaction_id=transaction_id,
            days_rented=days_rented,
            total_fee=total_fee,
            Amount_paid=""  # You can set this to an empty string or any default value you prefer
        )

        if request.method == 'POST' and form.validate_on_submit():
            # Get the amount paid from the form
            amount_paid = form.Amount_paid.data
            if amount_paid > total_fee:
                flash(f'Please enter a lower amount. The fee due is {total_fee}')
                return redirect(url_for('transactions.return_book', transaction_id= transaction_id))

            # Check if outstanding_debt is None, and if so, initialize it to 0
            if member.outstanding_debt is None:
                member.outstanding_debt = 0
            # Calculate the debt for this transaction based on the amount paid

            transaction_debt = total_fee - amount_paid
            # Check if outstanding_debt + transaction_debt exceeds 500
            if member.outstanding_debt + transaction_debt > 500:
                flash("Outstanding debt cannot exceed Rs. 500", "error")
                return redirect(url_for('transactions.issue_book', transaction_id=transaction_id))

            # Update the transaction table with returned_date, total_fee, and amount_paid
            transaction.return_date = return_date
            transaction.total_fee = total_fee
            transaction.amount_paid = amount_paid

            # Update member's outstanding debt
            member.outstanding_debt += transaction_debt  # Subtract the transaction_debt from the outstanding debt

            # Increase the available quantity of the returned book
            book = Book.query.get(transaction.book_id)
            book.Quantity += 1

            # Commit the changes to the database
            try:
                db.session.commit()
                flash("Book returned successfully!", "success")
                return redirect(url_for('transactions.issue_book', transaction_id=transaction_id))
            except SQLAlchemyError as exception:
                db.session.rollback()
                flash(f"An error occurred while committing to the database: {str(exception)}", "error")

    else:
        flash("Transaction not found.", "error")
        return redirect(url_for('transactions.view_transactions'))  # Redirect to transactions page

    # Render the return book form with prefilled values
    return render_template(
        'transaction/return_book.html',
        form=form,
        transaction_id=transaction_id,
        days_rented=days_rented,
        total_fee=total_fee,
        transaction=transaction
    )

# Route to view transactions
@app.route('/transactions', methods=['GET'])
def view_transactions():
    """
    A route for viewing transactions 
    """
    # Retrieve all transactions from the database
    transactions = Transaction.query.all()

    return render_template('transaction/view_transactions.html', transactions=transactions)
