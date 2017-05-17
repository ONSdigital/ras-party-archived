import os

''' This file is the main configuration for the RAS Party Service.
    It contains a full default configuration
    All configuration may be overridden by setting the appropriate environment variable name. '''

DEBUG = False
TESTING = False
CSRF_ENABLED = True
SECRET_KEY = 'this-really-needs-to-be-changed'
dbname = "ras_party"
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI', 'postgresql://ras_party:password@localhost:5431/postgres')

STATUS_CODES = ['ACTIVE', 'CREATED', 'SUSPENDED']

ENROLMENT_STATUS_CODES = ['ACTIVE', 'REDEEMED', 'REVOKED']

LEGAL_STATUS_CODES = ['COMMUNITY_INTEREST_COMPANY', 'CHARITABLE_INCORPORATED_ORGANISATION',
                      'INDUSTRIAL_AND_PROVIDENT_SOCIETY', 'GENERAL_PARTNERSHIP',
                      'LIMITED_LIABILITY_PARTNERSHIP', 'LIMITED_PARTNERSHIP',
                      'PRIVATE_LIMITED_COMPANY', 'PUBLIC_LIMITED_COMPANY',
                      'UNLIMITED_COMPANY', 'SOLE_PROPRIETORSHIP']

AUTHORIZATION_ENDPOINT = "https://www.facebook.com/dialog/oauth"  # Facebook Auth endpoint
TOKEN_ENDPOINT = "https://graph.facebook.com/oauth/access_token"  # Facebook token endpoint
ONS_OAUTH_PROTOCOL = os.environ.get('ONS_OAUTH_PROTOCOL', 'http://')
ONS_OAUTH_SERVER = os.environ.get('ONS_OAUTH_SERVER', 'localhost:8040')
RAS_PARTY_CLIENT_ID = os.environ.get('RAS_PARTY_CLIENT_ID', 'ons@ons.gov')
RAS_PARTY_CLIENT_SECRET = os.environ.get('RAS_PARTY_CLIENT_SECRET', 'password')
ONS_AUTHORIZATION_ENDPOINT = os.environ.get('ONS_AUTHORIZATION_ENDPOINT', '/web/authorize/')
ONS_TOKEN_ENDPOINT = os.environ.get('ONS_TOKEN_ENDPOINT', '/api/v1/tokens/')
ONS_ADMIN_ENDPOINT = os.environ.get('ONS_ADMIN_ENDPOINT', '/api/account/create')
RAS_DB_ERROR = "Error in the Party DB"
RAS_LOG_LEVEL = "DEBUG"
RAS_ENROLEMENT_CODE_NOT_FOUND = "Enrolment code not found"
RAS_BUSINESS_NOT_FOUND = "Business not found"
RAS_BUSINESS_ASSOCIATION_NOT_FOUND = "Business association not found"
