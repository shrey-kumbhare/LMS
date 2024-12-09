# Library Management System

## Description

This app allows a librarian to perfom CRUD operations on books and library members. It utilizes the Frappe API
to import books to the library

## Installation

1. Create a virtual environment

```
python -m venv venv

```

2. Activate the Virtual Environment

```
source venv/bin/activate

```

3. Install Dependencies

```
pip install -r requirements.txt

```

4. Set Environment Variables. Create a .env file in the project root directory

```
SECRET_KEY=YourSecretKey
DEBUG=True
DATABASE_URI=sqlite:///library.db

```

5. Initialize the Database . Create the initial database and apply migrations.

```
flask db init
flask db migrate
flask db upgrade
```

## Usage

### `app/` Directory

- **`routes/`**: This directory contains Python files that define different routes and views for your application.

  - **`book.py`**: Manages routes and views for book-related operations.
    Imports book using the Frappe API, adds book to the library database, allows Librarian
    to search for books, updates book details, deletes book details, and view all books
  - **`member.py`**: Handles routes and views for library member-related operations.
    Allows the librarian to search for members, update member details, view members,
    delete members and view all members
  - **`transaction.py`**: Contains routes and views for handling book transactions (borrowing and returning).
    Allows the librarian to issues ooks, return books, and view transactions

  - **`auth.py`**: Handles user-related routes and views (authentication, registration, homepage.).

-**`templates/'**: Stores HTML templates for rendering different pages.

- **`book/`**
  Contains:
- add_books.html for adding books to library
 ![add_books](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/098c8575-c783-4bf1-a89b-66dd897a0bfb)

- import_books.html for importing books using the frappe API
  ![Import_books](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/47acf3e0-986a-45b2-8c18-2c803254006d)

- delete_books.html for deleting books from the library
 ![delete_books](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/8873b28b-f8b1-4596-be93-5f3958a564e3)

- search_books.html for searching books in the library
 ![search_books](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/8ff3c4b0-3f7e-40ad-aea0-bf9122590ba1)
  
- update_books.html for updating book details
![update_books](https://github.com/roseMunyiri/Library-Management-App/as
sets/101321558/6406e4b5-945b-4257-b774-3c988c2e91da)

- **`member/`**
  Contains:
- add_members.html for adding members to the library
  ![add_member](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/17c5a879-32f8-4302-bb56-fefab7e731a4)

- all_members.html for viewing all members in the library
  ![all_members](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/2f305f11-0a1a-4885-aaf9-c291f277a438)

- delete_members.html for delting members from the library
  ![delete_membersPNG](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/6e69ca39-995a-4da2-a637-4b8cef2ccb31)
  
- search_members.html for searching for members in the library
 ![search_members](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/79cd6b9f-a378-48fa-a335-d0715b48ed63)
  
- update_members.html for updating member details
  ![update_members](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/1e514667-04ce-451d-8c64-cf6c18cfe418)
02a8fd2a7)


- **`transaction/`**
  Contains:
- issue_book.html for issuing books to members
![issue_book](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/dbd9e9e3-068e-4bf0-8c5a-20d3365081d8)
  
- return_book.html for returning books to library
![return_book](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/d9bfeee8-32d7-4734-877d-cf9be130a81f)
  
- view_trandactions.html for viewing all transations
![view_transactioons](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/85149604-1830-42fd-95d9-a0c4a4f735da)

- **`auth/`**
  Contains:

  - home.html for viewing the homepage
    ![Home](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/0510084c-b3fb-4915-8fa6-b9dc08fb389f)

  - register.html for user registration
  ![Register](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/34e5a337-bcf3-4926-8e0c-9fd3c1a6e3e9)

    
  - login.html for member login
 
    ![login](https://github.com/roseMunyiri/Library-Management-App/assets/101321558/2084a338-8fea-495d-a819-c8f9ecc28a19)


- **`static/`**
  Contains:
  - styles.css
### `models.py`
Defines the database models for the application, including models for books, members, and  transactions.


