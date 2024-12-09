print(__name__)

from app import create_app


app = create_app()

# Set up the application context
app.app_context().push()


# Clear the template cache
app.jinja_env.cache = {}

if __name__ == '__main__':
    app.run(debug=True)
