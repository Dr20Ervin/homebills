import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # Load SECRET_KEY from the .env file
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    config_dir = '/config'
    if not os.path.exists(config_dir):
        try: os.makedirs(config_dir)
        except OSError: pass

    logging.basicConfig(filename=os.path.join(config_dir, 'app.log'), level=logging.INFO)

    db_path = os.path.join(config_dir, 'homebills.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' 

    with app.app_context():
        from . import models
        db.create_all() 
    from .routes import main
    app.register_blueprint(main)

    return app