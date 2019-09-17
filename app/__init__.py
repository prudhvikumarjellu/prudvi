# app/__init__.py

from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import app_config
from middleware import logger, auth
from middleware.auth import auth_api_v1

db = SQLAlchemy()
BASE_URL_PREFIX = ''


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])

    ''' App initialisation '''
    db.init_app(app)

    # Enabling Migration Setup
    migrate = Migrate(app, db)

    # Enabling CORS
    CORS(app)

    ''' Accessing Configuration'''
    # print('SECRET_KEY', app_config[config_name].SECRET_KEY)
    print('URL_PREFIX', app.config['URL_PREFIX'])

    return app


def attach_middleware(app):
    # Enabling Logger
    app.wsgi_app = logger.LoggerMiddleware(app.wsgi_app)

    # JWT Authentication
    app.wsgi_app = auth.AuthMiddleware(app.wsgi_app)

    # Enabling Common url prefix Validator
    # app.wsgi_app = api_prefix.PrefixMiddleware(app.wsgi_app, prefix='/api/v')


def register_blueprints(app):
    from api.user.views import user_api

    if BASE_URL_PREFIX:
        app.register_blueprint(user_api, url_prefix=BASE_URL_PREFIX)
        app.register_blueprint(auth_api_v1, url_prefix=BASE_URL_PREFIX)
    else:
        app.register_blueprint(user_api)
        app.register_blueprint(auth_api_v1)

    # Listing all API endpoints
    print(app.url_map)
