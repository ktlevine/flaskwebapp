from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, makedirs
from flask_login import LoginManager
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'OutsideBrandsSecretKey1234'
    
    # Use DATABASE_URL environment variable for Heroku PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///database.db').replace('postgres://', 'postgresql://')

    db.init_app(app)
    migrate.init_app(app, db)

    # Ensure the website directory exists
    if not path.exists('website'):
        print("Creating 'website' directory")
        makedirs('website')

    # Import and register blueprints
    from .views import views as views_blueprint
    from .auth import auth as auth_blueprint

    app.register_blueprint(views_blueprint, url_prefix='/')
    app.register_blueprint(auth_blueprint, url_prefix='/')

    from .models import User, Bike

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    with app.app_context():
        db.create_all()
        print('Database created')
