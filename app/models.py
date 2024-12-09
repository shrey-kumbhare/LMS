from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from sqlalchemy import Integer, String, Boolean, Float, Date, ForeignKey,UniqueConstraint
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app as app
from app import db, login_manager


class Member(UserMixin, db.Model):
    __tablename__ = 'members'

    id = db.Column(Integer, unique=True, primary_key=True)
    username = db.Column(String(20), unique=True, nullable=False)
    fullname = db.Column(String(20), nullable=False)
    email = db.Column(String(20), unique=True, nullable=False)
    outstanding_debt = db.Column(db.Float)
    hash_password = db.Column(String(150))


    def create_password(self, password):

        """
        Create a hashed password and set it for the member.
        """
        hashed_password = generate_password_hash(password)
        self.hash_password = hashed_password


    def verify_password(self, password):
        """
        Verify if a given plain-text password matches the hashed password stored for the member.

        """
        return check_password_hash(self.hash_password, password)

    def __repr__(self):
        """
        Returns a string representation of a user object
        """
        return f'<Member(username={self.username}), email={self.email}>'

# Query  database for user id 
@login_manager.user_loader
def load_user(id):
    return Member.query.get(int(id))

class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(20), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    isbn = db.Column(db.String(20), nullable=False, unique=True)
    publisher = db.Column(db.String(150), nullable=False)
    Quantity = db.Column(db.Integer, default=0)



    def __repr__(self):

        """
        Returns a string representation of a book object
        """
        return f'<Book(title={self.title}), author={self.author}, isbn={self.isbn}, publisher={self.publisher}>'

class Transaction(db.Model):
    __tablename__ = 'transaction'

    transaction_id = db.Column(Integer, primary_key=True)
    book_id = db.Column(Integer, ForeignKey('books.id'), nullable=True)
    member_id = db.Column(Integer, ForeignKey('members.id'), nullable=True)
    borrowed_date = db.Column(Date, nullable=True)
    return_date = db.Column(Date)
    total_fee = db.Column(Float)
    amount_paid = db.Column(Float)
 
    # Define relationships with member and book
    member = db.relationship('Member', backref='transactions')
    book = db.relationship('Book', backref='transactions')

    def __repr__(self):
        return f'''<Transaction(book_id={self.book_id}), 
                      member_id={self.member_id}, 
                      borrowed_date={self.borrowed_date}, 
                      return_date={self.returned_date},
                      total_fee={self.total_fee}
                      amount_paid={self.amount_paid}>'''

