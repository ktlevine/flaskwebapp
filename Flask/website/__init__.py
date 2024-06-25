from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path, makedirs
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'OutsideBrandsSecretKey1234'
    db_path = path.join(path.abspath('website'), DB_NAME)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://udjdpu6brkaejf:pc75ffc600d0fc0c2312e18f6720c6db58a69a359b750d1d34fcbf3ce8b9d337b@c5hilnj7pn10vb.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/dapgtn38oqjiq0'
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
    db_path = path.join(path.abspath('website'), DB_NAME)
    if not path.exists(db_path):
        with app.app_context():
            db.create_all()
            print(f'Created Database at {db_path}')
    else:
        print(f"Database already exists at {db_path}")
