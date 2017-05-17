"""
The main module which starts the server
"""
import logging
import os

from flask import request, Response, make_response, jsonify, Flask
from flask_cors import CORS

import settings
from controllers import create_business, create_respondent_db, get_enrolment_code_response, \
    get_business_by_ref_response, get_business_associations_by_business_id_response, \
    get_business_associations_by_respondent_id_response, get_business_by_id_response, \
    set_enrolment_code_as_redeemed_from_db, set_verification_token_as_redeemed_from_db
from authentication.decorator import authorization_required
from database import db
from validators.legal import LegalStatus
from validators.phone_number import PhoneNumber
from validators.required_keys import RequiredKeys
from validators.status_code import StatusCode
from exception import DBError

# Enable cross-origin requests
app = Flask(__name__)
CORS(app)

if 'APP_SETTINGS' in os.environ:
    app.config.from_object(os.environ['APP_SETTINGS'])

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = settings.SQLALCHEMY_DATABASE_URI
db.init_app(app)


@app.route('/enrolment-codes/<string:enrolment_code>', methods=['GET'])
@authorization_required('ps.read')
def get_enrolment_code(enrolment_code):
    """
    Locate an enrolment_code by its iac.
    :param enrolment_code: String
    :return: Http Response
    """
    logging.info("get_enrolment_code with enrolment_code: {}".format(enrolment_code))
    response = get_enrolment_code_response(enrolment_code)
    return response


@app.route('/enrolment-codes/<string:enrolment_code>', methods=['PUT'])
@authorization_required('ps.write')
def set_enrolment_code_as_redeemed(enrolment_code):
    """
    Mark an enrolment_code as redeemed by its iac.
    :param enrolment_code: String, respondent_urn: String
    :return: Http Response
    """
    respondent_urn = 'urn:uk.gov.ons:id:respondent:1111'
    response = set_enrolment_code_as_redeemed_from_db(enrolment_code, respondent_urn)
    return response


@app.route('/businesses/ref/<string:business_ref>', methods=['GET'])
@authorization_required('ps.read')
def get_business_by_ref(business_ref):
    """
    Locate a business by its business_ref.
    :param business_ref: String
    :return: Http Response
    """
    logging.info("get_business_by_ref with business_ref: {}".format(business_ref))
    response = get_business_by_ref_response(business_ref)
    return response


@app.route('/businesses/id/<string:business_id>', methods=['GET'])
@authorization_required('ps.read')
def get_business_by_id(business_id):
    """
    Locate a business by its business_id.
    :param business_id: String
    :return: Http Response
    """
    logging.info("get_business_by_id with business_id: {}".format(business_id))
    response = get_business_by_id_response(business_id)
    return response


@app.route('/businesses/id/<string:business_id>/business-associations', methods=['GET'])
@authorization_required('ps.read')
def get_business_associations_by_business_id(business_id):
    """
    Locate a business associations by business_id.
    :param business_id: String, classifier: String
    :return: Http Response
    """
    logging.info("get_business_associations_by_business_id with business_id: {}".format(business_id))
    response = get_business_associations_by_business_id_response(business_id)
    return response


@app.route('/respondents/id/<string:respondent_id>/business-associations', methods=['GET'])
@authorization_required('ps.read')
def get_business_associations_by_respondent_id(respondent_id):
    """
    Locate a business associations by its respondent_id.
    :param business_id: String, classifier: String
    :return: Http Response
    """
    logging.info("get_business_associations_by_respondent_id with respondent_id: {}".format(respondent_id))
    response = get_business_associations_by_respondent_id_response(respondent_id)
    return response


@app.route('/businesses/', methods=['POST'])
@authorization_required('ps.write')
def create_businesses():
    """
    This endpoint creates a business record, from the POST data.
    It takes in a parameter list for a user as:
    :param
        JSON representation of the business

    :return: Http response 200
        id  urn:ons.gov.uk:id:business:001.234.56789
    """

    logging.info("creating a business")
    json = request.get_json()

    if json:
        required_keys = ["businessRef", "name", "addressLine1", "city", "postcode"]
        validators = [LegalStatus(json), PhoneNumber(json), RequiredKeys(required_keys, json)]
        response, is_valid = validate_json(validators)

        if is_valid:
            response = create_business(json, response)
        return response

    return jsonify({"message": "Please provide a valid Json object.",
                    "hint": "you may need to pass a content-type: application/json header"}), 400


def validate_json(validators):
    is_valid = True
    response = make_response("")
    for validate in validators:
        if not validate.is_valid():
            response = Response(response="{}".format(validate.get_message()), status=404, mimetype="text/html")
            is_valid = False

    return response, is_valid


@app.route('/respondents/', methods=['POST'])
@authorization_required('ps.write')
def create_respondent():

    """
    This endpoint creates a respondent record, from the POST data.
    It takes in a parameter list for a user as:
    :param
        emailAddress
        firstName
        lastName
        telephone
        status [ ACTIVE | CREATED | ACTIVE | SUSPENDED ]

    :return: Http response 200
        id  urn:ons.gov.uk:id:respondent:001.234.56789

    The email must be unique for this user.
    """

    logging.info("respondents/create_respondent()")

    json = request.get_json()
    if json:
        required_keys = ["emailAddress", "firstName", "lastName", "telephone", "status", "enrolmentCode"]
        validators = [StatusCode(json), PhoneNumber(json), RequiredKeys(required_keys, json)]
        response, is_valid = validate_json(validators)

        if is_valid:
            response = create_respondent_db(json, response)

        return response

    return jsonify({"message": "Please provide a valid Json object.",
                    "hint": "you may need to pass a content-type: application/json header"}), 400


@app.route('/verification-tokens/<string:verification_token>', methods=['PUT'])
@authorization_required('ps.write')
def set_verification_token_as_redeemed(verification_token):
    """
    Mark a verification_token as redeemed.
    :param verification_token: String
    :return: Http Response
    """

    logging.info("respondents/create_respondent()")
    response = set_verification_token_as_redeemed_from_db(verification_token)
    return response


@app.errorhandler(DBError)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5062))
    app.run(host='0.0.0.0', port=PORT, debug=False)
