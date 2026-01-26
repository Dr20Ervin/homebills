import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    
    # 1. Load Secret Key
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-dev-key')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Setup Config Directory (for logs and SQLite fallback)
    config_dir = '/config'
    if not os.path.exists(config_dir):
        try: 
            os.makedirs(config_dir)
        except OSError: 
            pass

    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # 3. Database Connection Logic
    db_type = os.environ.get('DATABASE', 'SQLite')

    if db_type == 'psql':
        # Read PostgreSQL variables from docker-compose environment
        user = os.environ.get('PSQL_USER', 'hb_user')
        pw   = os.environ.get('PSQL_PASSWORD', 'secure_password')
        host = os.environ.get('PSQL_HOST', 'db')
        name = os.environ.get('PSQL_DB', 'homebills_db')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{user}:{pw}@{host}/{name}'
        logging.info("Database Mode: PostgreSQL")
    else:
        # Fallback to SQLite (Default)
        db_path = os.path.join(config_dir, 'homebills.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        logging.info("Database Mode: SQLite")


    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' 

    with app.app_context():
        from . import models
        db.create_all() 
        
    from .routes import main
    app.register_blueprint(main)

    return app