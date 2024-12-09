from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

# Create SQLAlchemy instance without initializing it yet
db = SQLAlchemy()
migrate = Migrate(db)
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app():
    app = Flask(__name__, template_folder='templates')
    app.config.from_object(Config)

    # Initialize extensions within the application context
    with app.app_context():
        # Initialize the SQLAlchemy extension
        db.init_app(app)

        # Initialize flask migrate
        migrate.init_app(app, db)

        # Initialize the login_manager and set the login view
        login_manager.init_app(app)
       

        # Register blueprints
        from app.routes.auth import bp as auth_bp
        app.register_blueprint(auth_bp)

        from app.routes.book import bp as book_bp
        app.register_blueprint(book_bp)

        from app.routes.members import bp as member_bp
        app.register_blueprint(member_bp)

        from app.routes.transactions import bp as transaction_bp
        app.register_blueprint(transaction_bp)


    return app
