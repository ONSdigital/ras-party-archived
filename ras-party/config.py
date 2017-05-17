"""
This module hosts the config setup for our project
"""

import os
import connector

# ENV VARIABLES BELOW, SET THESE ON YOUR TERMINAL
# export APP_SETTINGS=config.Config
# export FLASK_APP=app.py

# Default values
if "APP_SETTINGS" not in os.environ:
    os.environ["APP_SETTINGS"] = "config.Config"


class Config(object):
    """
    Base config class
    """
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = 'this-really-needs-to-be-changed'
    dbname = "ras_party"
    #SQLALCHEMY_DATABASE_URI = "postgresql://" + dbname + ":password@localhost:5431/postgres"
    SQLALCHEMY_DATABASE_URI = connector.getDatabaseUri()

class ProductionConfig(Config):
    """
    Production config class
    """
    DEBUG = False


class StagingConfig(Config):
    """
    Staging config class
    """
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    """
    Development config class
    """
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    """
    Testing config class
    """
    TESTING = True


class PartyService(Config):
    """
    This class is used to configure parameters that may be used in our microservice.
    This is temporary until an admin config feature is added to allow manual config of the microservice
    """

    STATUS_CODES = ['ACTIVE', 'CREATED', 'SUSPENDED']         # used in registering a new user


class OAuthConfig(Config):
    """
    This class is used to configure OAuth2 parameters for the microservice.
    This is temporary until an admin config feature
    is added to allow manual config of the microservice
    """

    #ONS_OAUTH_PROTOCOL = "http://"
    #ONS_OAUTH_SERVER = "localhost:8000"
    #RAS_FRONTSTAGE_CLIENT_ID = "onc@onc.gov"
    #RAS_FRONTSTAGE_CLIENT_SECRET = "password"
    #ONS_AUTHORIZATION_ENDPOINT = "/web/authorize/"
    #ONS_TOKEN_ENDPOINT = "/api/v1/tokens/"
    #ONS_ADMIN_ENDPOINT = '/api/account/create'

    ONS_OAUTH_PROTOCOL = os.environ.get('ONS_OAUTH_PROTOCOL', 'http://')
    ONS_OAUTH_SERVER = os.environ.get('ONS_OAUTH_SERVER', 'localhost:8040')
    RAS_PARTY_CLIENT_ID = os.environ.get('RAS_PARTY_CLIENT_ID', 'ons@ons.gov')
    RAS_PARTY_CLIENT_SECRET = os.environ.get('RAS_PARTY_CLIENT_SECRET', 'password')
    ONS_AUTHORIZATION_ENDPOINT = os.environ.get('ONS_AUTHORIZATION_ENDPOINT', '/web/authorize/')
    ONS_TOKEN_ENDPOINT = os.environ.get('ONS_TOKEN_ENDPOINT', '/api/v1/tokens/')
    ONS_ADMIN_ENDPOINT = os.environ.get('ONS_ADMIN_ENDPOINT', '/api/account/create')

