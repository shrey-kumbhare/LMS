"""
A module that allows the librarian to search for members, update member details, view members, 
delete members and view all members
"""
from flask import Blueprint, flash, redirect, url_for, render_template, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import InputRequired, Length, Email
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash
from app.models import Member, db

# Create blueprint
bp = Blueprint('member', __name__)

class SearchMembersForm(FlaskForm):
    """
    Class that creates a form object to view member details
    """
    search = StringField('Search by name or ID', validators=[InputRequired(), Length(max=255)])
    submit = SubmitField('Delete')
    submit = SubmitField('Edit')

class UpdateMembersForm(FlaskForm):
    """
    Class that creates a form to edit member details
    """
    username = StringField('Username', validators=[InputRequired(), Length(max=255)])
    fullname = StringField('Fullname', validators=[InputRequired(), Length(max=255)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    outstanding_debt = IntegerField('outstanding debt', validators=[InputRequired()])
    submit = SubmitField('Update')

class DeleteMembersForm(FlaskForm):
    """
    Class that creates a form object to delete member details
    """
    username = StringField('Username', validators=[InputRequired(), Length(max=255)])
    fullname = StringField('Fullname', validators=[InputRequired(), Length(max=255)])
    email = StringField('Email', validators=[InputRequired(), Email()])
    outstanding_debt = IntegerField('outstanding debt', validators=[InputRequired()])
    submit = SubmitField('Delete')

class AddMembersForm(FlaskForm):
    """
    Class that creates a form object to add members
    """
    username = StringField('Username', validators=[InputRequired()])
    fullname = StringField('Full Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired(), Email()])
    submit = SubmitField('Add Member')


# Route to search member details
@bp.route('/search-members', methods=['POST', 'GET'])
def search_members():

    """
    A route to search for a specific member
    """
    form = SearchMembersForm()

    members_list = []
    if request.method == 'POST':
        search_query = form.search.data

        if search_query:
            # Attempt to query by ID
            if search_query.isdigit():
                member_id = int(search_query)
                members_list = Member.query.filter(Member.id == member_id).all()
            else:
                # If it's not a valid integer, query by name, email, or username
                members_list = Member.query.filter(
                    (Member.fullname.like(f'%{search_query}%')) |
                    (Member.username.like(f'%{search_query}%')) |
                    (Member.email.like(f'%{search_query}%'))
                ).all()

            if not members_list:
                flash('Member not found!')
                return redirect(url_for('member.search_members'))
    return render_template('member/search_members.html', form=form, members_list=members_list)

# Route to edit member details
@bp.route('/update-members/<int:id>', methods=['POST', 'GET'])
def update_members(id):
    """
    A route to update member details
    """
    print(f"Received ID: {id}")  # Add this line to check the received ID
    member_to_update = Member.query.get(id)
    form = UpdateMembersForm()

    print(f"Member: {member_to_update.id}")

    if member_to_update:
        if request.method == 'GET':
            # Prefill the form with member details
            form.username.data = member_to_update.username
            form.fullname.data = member_to_update.fullname
            form.email.data = member_to_update.email
            form.outstanding_debt.data = member_to_update.outstanding_debt
            print(f"debt: {member_to_update.email}")

        if form.validate_on_submit() and request.method == "POST":
            # Update member details based on form data
            member_to_update.username = form.username.data 
            member_to_update.fullname = form.fullname.data
            member_to_update.email = form.email.data
            member_to_update.outstanding_debt = form.outstanding_debt.data  
            print(f"debt: {member_to_update.email}")
            if form.errors:
                print("Form errors:", form.errors)
            try:
                db.session.commit()
                print("Database commit successful") 
                flash(f"{member_to_update.fullname}'s details updated successfully", "success")
                return redirect(url_for('member.search_members'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred while updating member details: {str(e)}", "error")
        else:
            print("form not validated")

        return render_template('member/update_members.html', form=form, member_to_update=member_to_update, id=id)


# Route to delete members
@bp.route('/delete-members/<int:id>', methods=['GET', 'POST'])
def delete_members(id):
    """
    A route to delete members
    """
    member_to_delete = Member.query.get(id)
    form = DeleteMembersForm(username=member_to_delete.username, fullname=member_to_delete.fullname, email=member_to_delete.email, outstanding_debt=member_to_delete.outstanding_debt)

    if member_to_delete:
        if request.method == 'POST':
            try:
                db.session.delete(member_to_delete)
                db.session.commit()
                flash(f"{member_to_delete.fullname} successfully deleted from the library", "success")
                return redirect(url_for('member.search_members'))
            except SQLAlchemyError as exception:
                db.session.rollback()
                flash(f"An error occurred while deleting the member: {str(exception)}", "error")
                return redirect(url_for('member.search_members'))

    return render_template('member/delete_members.html', form=form, member_to_delete=member_to_delete)

# Route to add a new member
@bp.route('/add-members', methods=['GET', 'POST'])
def add_member():
    """
    A route to add new members
    """
    form = AddMembersForm ()
    if request.method == 'POST':
        # Get member information from the form
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        # Generate a temporary password
        temporary_password = 'temporary_password'
        hashed_password = generate_password_hash(temporary_password)

        # Check if Username already exists
        existing_member = Member.query.filter_by(username=username).first()
        if existing_member:
            flash("This username is taken")
        else:
            # Create a new member
            new_member = Member(username=username, fullname=fullname, email=email,
                                hash_password=hashed_password)
        

        try:
            # Add the new member to the database
            db.session.add(new_member)
            db.session.commit()
            flash(f"Member '{username}' successfully added.", "success")
            return redirect(url_for('member.search_members'))
        except SQLAlchemyError as exception:
            db.session.rollback()
            flash(f"An error occurred while adding the member: {str(exception)}", "error")

    return render_template('member/add_members.html', form=form)

@bp.route('/all-members')
def all_members():
    """ 
    A route for viewing all members in the database
    """
    all_members = Member.query.all()
    return render_template('member/all_members.html', all_members=all_members)
