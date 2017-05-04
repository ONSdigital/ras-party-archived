"""
The main module which starts the server
"""

import ast
import hashlib
import os
import sys
import uuid
import logging
from logging import Formatter
from logging.handlers import RotatingFileHandler


from flask import request, Response, send_from_directory, make_response, jsonify, Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import exc
from jose import JWTError
from jwt import decode
from json import JSONEncoder
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException
from config import PartyService
from random import randint

# Enable cross-origin requests
app = Flask(__name__)
CORS(app)


#
# http://docs.sqlalchemy.org/en/latest/core/type_basics.html
#
# data_table = Table('data_table', metadata,
#    Column('id', Integer, primary_key=True),
#    Column('data', JSON)
# )
#
"""
[{TO BE DONE}]
"""

if 'APP_SETTINGS' in os.environ:
    app.config.from_object(os.environ['APP_SETTINGS'])

# app.config.from_object("config.StagingConfig")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# NB this cirtular import needs resolving.
# There are ways of doing this, so we'll need to arrive at a decent solution.
from models import *


def validate_uri(uri, id_type):
    """
    This function verifies if a resource uri string is in the correct
    format. it returns True or False. This function does not check
    if the uri is present in the database or not.

    :param uri: String
    :param id_type: String
    :return: Boolean
    """

    app.logger.info("validate_uri uri: {}, id_type: {}".format(uri, id_type))
    app.logger.debug("Validating our URI: {}".format(uri))

    urn_prefix = 'urn'
    urn_ons_path = 'ons.gov.uk'
    urn_id_str = 'id'
    # urn_overall_digit_len = 13
    # urn_first_digit_len = 3
    # urn_second_digit_len = 3
    # urn_third_digit_len = 5

    try:

        arr = uri.split(':')
        sub_arr = arr[4].split('.')

        if arr[0] == urn_prefix \
                and arr[1] == urn_ons_path \
                and arr[2] == urn_id_str \
                and arr[3] == id_type:
            #     and len(arr[4]) == urn_overall_digit_len \
            #     and sub_arr[0].isdigit and len(sub_arr[0]) == urn_first_digit_len \
            #     and sub_arr[1].isdigit and len(sub_arr[1]) == urn_second_digit_len \
            #     and sub_arr[2].isdigit and len(sub_arr[2]) == urn_third_digit_len:
            app.logger.debug("URI is well formed': {}".format(uri[0:14]))
            return True
        else:
            app.logger.warning("URI is malformed: {}. It should be: {}".format(uri[0:14], urn_ons_path))
            return False

    except:
        app.logger.warning("URI is malformed: {}. It should be: {}".format(uri[0:14], urn_ons_path))
        return False


def generate_urn(id_type):

    # TODO: write a proper URN generator

    new_sequence = randint(0, 99999999999)
    new_urn = "urn:ons.gov.uk:id:" + id_type + ":" + str(new_sequence)
    return new_urn


def get_case_context(enrolment_code):

    # TODO: write a proper case context fn()

    enrolment_codes = (db.session.query(EnrolmentCode, Business)
                       .filter(EnrolmentCode.business_id == Business.id)
                       .filter(EnrolmentCode.iac == enrolment_code))

    object_list = [[enc.survey_id, bus.id]
                   for enc, bus in enrolment_codes]

    if object_list:
        survey_id = object_list[0][0]
        business_id = object_list[0][1]
    else:
        survey_id = None
        business_id = None

    return survey_id, business_id


def validate_phone_number(telephone):

    # A small helper function which helps you validate that a string is a valid phone number

    if len(telephone) > 16:
        return False
    try:
        print "Checking this is a valid GB Number"
        input_number = phonenumbers.parse(telephone, "GB")  # Tell the parser we are looking for a GB number

        if not (phonenumbers.is_possible_number(input_number)):
            return False

        if not (phonenumbers.is_valid_number(input_number)):
            return False
    except NumberParseException:
        print " There is a number parse exception in the phonenumber field"
        return False

    return True


def validate_status_code(status):

    if status in PartyService.STATUS_CODES:
        return True
    else:
        return False


def validate_legal_status_code(legalStatus):

    if legalStatus in PartyService.LEGAL_STATUS_CODES:
        return True
    else:
        return False


def validate_scope(jwt_token, scope_type):
    """
    This function checks a jwt tokem for a required scope type.

    :param jwt_token: String
    :param scope_type: String
    :return: Boolean
    """

    app.logger.info("validate_scope jwt_token: {}, scope_type: {}".format(jwt_token, scope_type))

    # Make sure we can decrypt the token and it makes sense

    return_val= False
    try:
        decrypted_jwt_token = decode(jwt_token)
        if decrypted_jwt_token['scope']:
            for user_scope_list in decrypted_jwt_token['scope']:
                if user_scope_list == scope_type:
                    app.logger.debug('Valid JWT scope.')
                    return_val=True

        if not return_val:
            app.logger.warning('Invalid JWT scope.')
            return False

        if decrypted_jwt_token['expires_at']:
            # We have a time stamp so check this token has not expired
            #TODO Add UTC Time stamp validation
            app.logger.info('Token: {} has a UTC time stamp of: {}'.format(decrypted_jwt_token['access_token'],decrypted_jwt_token['expires_at']))
        else:
            # We don't have a time stamp
            app.logger.warning('Token has expired for token Value: {}'.format(decrypted_jwt_token['access_token']))
            return False

        return return_val

    except JWTError:
        app.logger.warning('JWT scope could not be validated.')
        return False

    except KeyError:
        app.logger.warning('JWT scope could not be validated.')
        return False


@app.route('/enrolment-codes/<string:enrolment_code>', methods=['GET'])
def get_enrolment_code(enrolment_code):
    """
    Locate an enrolment_code by its iac.
    :param enrolment_code: String
    :return: Http Response
    """

    app.logger.info("get_enrolment_code with enrolment_code: {}".format(enrolment_code))

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.read'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    try:
        app.logger.debug("Querying DB in get_enrolment_code")

        app.logger.debug("Querying DB with get_enrolment_code:{}".format(enrolment_code))

        enrolment_codes = (db.session.query(EnrolmentCode, Business)
                          .filter(EnrolmentCode.business_id == Business.id)
                          .filter(EnrolmentCode.respondent_id == None)
                          .filter(EnrolmentCode.status == 'ACTIVE')
                          .filter(EnrolmentCode.iac == enrolment_code))

        object_list = [[enc.survey_id,
                        bus.name]
                       for enc, bus in enrolment_codes]

    except exc.OperationalError:
        app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
        response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
        return response

    if not object_list:
        app.logger.info("Object list is empty for get_enrolment_code")
        response = Response(response="Enrolment code not found", status=404, mimetype="text/html")
        return response

    jobject_list = JSONEncoder().encode(object_list)
    response = Response(response=jobject_list, status=200, mimetype="collection+json")
    return response


@app.route('/enrolment-codes/redeem/<string:enrolment_code>', methods=['PUT'])
def set_enrolment_code_as_redeemed(enrolment_code, respondent_urn=None):
    """
    Mark an enrolment_code as redeemed by its iac.
    :param enrolment_code: String, respondent_urn: String
    :return: Http Response
    """

    if not respondent_urn:
        respondent_urn = request.args.get('respondentId')

    app.logger.info("set_enrolment_code_as_redeemed with enrolment_code: {}, respondent: {}"
                    .format(enrolment_code, respondent_urn))

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.write'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    try:
        app.logger.debug("Querying DB in set_enrolment_code_as_redeemed")

        app.logger.debug("Querying DB with set_enrolment_code_as_redeemed:{}".format(enrolment_code))

        enrolment_codes = (db.session.query(EnrolmentCode)
                          .filter(EnrolmentCode.respondent_id == None)
                          .filter(EnrolmentCode.status == 'ACTIVE')
                          .filter(EnrolmentCode.iac == enrolment_code))

        existing_enrolment_code = [[enc.id, enc.business_id, enc.survey_id, enc.iac, enc.status]
                                    for enc in enrolment_codes]

        if not existing_enrolment_code:
            app.logger.info("Enrolment code not found for set_enrolment_code_as_redeemed")
            response = Response(response="Enrolment code not found", status=400, mimetype="text/html")
            return response

        respondents = (db.session.query(Respondent)
                       .filter(Respondent.party_id == respondent_urn))

        respondent_id = [[res.id]
                         for res in respondents]

        if not respondent_id:
            app.logger.info("Respondent not found for set_enrolment_code_as_redeemed")
            response = Response(response="Respondent not found", status=400, mimetype="text/html")
            return response

        new_enrolment_code = EnrolmentCode(id=existing_enrolment_code[0][0],
                                           respondent_id=respondent_id[0][0],
                                           business_id=existing_enrolment_code[0][1],
                                           survey_id=existing_enrolment_code[0][2],
                                           iac=existing_enrolment_code[0][3],
                                           status='REDEEMED')

        db.session.merge(new_enrolment_code)
        db.session.commit()

    except exc.OperationalError:
        app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
        response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
        return response

    response = Response(response="Enrolment code redeemed", status=200, mimetype="text/html")
    return response


@app.route('/businesses/ref/<string:business_ref>', methods=['GET'])
def get_business_by_ref(business_ref):
    """
    Locate a business by its business_ref.
    :param business_ref: String
    :return: Http Response
    """

    app.logger.info("get_business_by_ref with business_ref: {}".format(business_ref))

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.read'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    try:
        app.logger.debug("Querying DB in get_business_by_ref")

        app.logger.debug("Querying DB with business_ref:{}".format(business_ref))

        object_list = [[rec.business_ref, rec.party_id, rec.name, rec.trading_name,
                        rec.enterprise_name, rec.contact_name, rec.address_line_1,
                        rec.address_line_2, rec.address_line_3, rec.city, rec.postcode,
                        rec.telephone, rec.employee_count, rec.facsimile, rec.fulltime_count,
                        rec.legal_status, rec.sic_2003, rec.sic_2007, rec.turnover]
                       for rec in
                       Business.query
                       .filter(Business.business_ref == business_ref)]

    except exc.OperationalError:
        app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
        response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
        return response

    if not object_list:
        app.logger.info("Object list is empty for get_business_by_ref")
        response = Response(response="Business(es) not found", status=404, mimetype="text/html")
        return response

    jobject_list = JSONEncoder().encode(object_list)
    response = Response(response=jobject_list, status=200, mimetype="collection+json")
    return response


@app.route('/businesses/id/<string:business_id>', methods=['GET'])
def get_business_by_id(business_id):
    """
    Locate a business by its business_id.
    :param business_id: String
    :return: Http Response
    """

    app.logger.info("get_business_by_id with business_id: {}".format(business_id))

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.read'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    # if not validate_uri(business_id, 'business'):
    #     res = Response(response="Invalid URI", status=404, mimetype="text/html")
    #     return res

    try:
        app.logger.debug("Querying DB in get_business_by_id")

        app.logger.debug("Querying DB with business_id:{}".format(business_id))

        object_list = [[rec.business_ref, rec.party_id, rec.name, rec.trading_name,
                        rec.enterprise_name, rec.contact_name, rec.address_line_1,
                        rec.address_line_2, rec.address_line_3, rec.city, rec.postcode,
                        rec.telephone, rec.employee_count, rec.facsimile, rec.fulltime_count,
                        rec.legal_status, rec.sic_2003, rec.sic_2007, rec.turnover]
                       for rec in
                       Business.query
                       .filter(Business.party_id == business_id)]

    except exc.OperationalError:
        app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
        response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
        return response

    if not object_list:
        app.logger.info("Object list is empty for get_business_by_id")
        response = Response(response="Business(es) not found", status=404, mimetype="text/html")
        return response

    jobject_list = JSONEncoder().encode(object_list)
    response = Response(response=jobject_list, status=200, mimetype="collection+json")
    return response


@app.route('/businesses/id/<string:business_id>/business-associations', methods=['GET'])
def get_business_associations_by_business_id(business_id):
    """
    Locate a business associtaions by business_id.
    :param business_id: String, classifier: String
    :return: Http Response
    """

    app.logger.info("get_business_associations_by_business_id with business_id: {}".format(business_id))

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.read'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    if not validate_uri(business_id, 'business'):
        res = Response(response="Invalid URI", status=404, mimetype="text/html")
        return res

    try:
        app.logger.debug("Querying DB in get_business_associations_by_business_id")

        app.logger.debug("Querying DB with business_id:{}".format(business_id))

        business_associations = (db.session.query(Business, BusinessAssociation, Respondent, Enrolment)
                                .filter(Business.id == BusinessAssociation.business_id)
                                .filter(BusinessAssociation.respondent_id == Respondent.id)
                                .filter(BusinessAssociation.id == Enrolment.business_association_id)
                                .filter(Business.party_id == business_id))

        object_list = [[bus.business_ref, bus.party_id, bus.name,
                        bua.status,
                        res.email_address, res.first_name, res.last_name,
                        enr.survey_id]
                       for bus, bua, res, enr in business_associations]

    except exc.OperationalError:
        app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
        response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
        return response

    if not object_list:
        app.logger.info("Object list is empty for get_business_associations_by_business_id")
        response = Response(response="Association(s) not found", status=404, mimetype="text/html")
        return response

    jobject_list = JSONEncoder().encode(object_list)
    response = Response(response=jobject_list, status=200, mimetype="collection+json")
    return response


@app.route('/respondents/id/<string:respondent_id>/business-associations', methods=['GET'])
def get_business_associations_by_respondent_id(respondent_id):
    """
    Locate a business associtaions by its respondent_id.
    :param business_id: String, classifier: String
    :return: Http Response
    """

    app.logger.info("get_business_associations_by_respondent_id with respondent_id: {}".format(respondent_id))

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.read'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    if not validate_uri(respondent_id, 'respondent'):
        res = Response(response="Invalid URI", status=404, mimetype="text/html")
        return res

    try:
        app.logger.debug("Querying DB in get_business_associations_by_respondent_id")

        app.logger.debug("Querying DB with respondent_id:{}".format(respondent_id))

        business_associations = (db.session.query(Business, BusinessAssociation, Respondent, Enrolment)
                                .filter(Business.id == BusinessAssociation.business_id)
                                .filter(BusinessAssociation.respondent_id == Respondent.id)
                                .filter(BusinessAssociation.id == Enrolment.business_association_id)
                                .filter(Respondent.party_id == respondent_id))

        object_list = [[bus.business_ref, bus.party_id, bus.name,
                        bua.status,
                        res.email_address, res.first_name, res.last_name,
                        enr.survey_id]
                       for bus, bua, res, enr in business_associations]

    except exc.OperationalError:
        app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
        response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
        return response

    if not object_list:
        app.logger.info("Object list is empty for get_business_associations_by_respondent_id")
        response = Response(response="Association(s) not found", status=404, mimetype="text/html")
        return response

    jobject_list = JSONEncoder().encode(object_list)
    response = Response(response=jobject_list, status=200, mimetype="collection+json")
    return response


@app.route('/businesses/', methods=['POST'])
def create_businesses():
    """
    This endpoint creates a business record, from the POST data.
    It takes in a parameter list for a user as:
    :param
        JSON representation of the business

    :return: Http response 200
        id  urn:ons.gov.uk:id:business:001.234.56789
    """

    app.logger.info("businesses/create_business()")

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.write'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    party_respondent = []

    json = request.json
    if json:
        response = make_response("")

        party_respondent.append(request.json)
        response.headers["location"] = "/respondents/"

        # Check that we have all the correct attributes in our json object.
        try:

            json["businessRef"]
            json["name"]
            json["addressLine1"]
            json["city"]
            json["postcode"]

        except KeyError:
            app.logger.warning("""Party Service POST did not contain correct mandatory
                               parameters in it's JSON payload: {}""".format(str(json)))
            res = Response(response="invalid input, object invalid", status=404, mimetype="text/html")
            return res

        if not validate_legal_status_code(json["legalStatus"]):
            app.logger.warning("""Party Service POST did not contain a valid legal status code in the legal status field.
                               Received: {}""".format(json['legalStatus']))
            res = Response(response="invalid status code, object invalid", status=404, mimetype="text/html")
            return res

        if not validate_phone_number(json["telephone"]):
            app.logger.warning("""Party Service POST did not contain a valid UK phone number in the telephone field.
                               Received: {}""".format(json['telephone']))
            res = Response(response="invalid phone number, object invalid", status=404, mimetype="text/html")
            return res

        try:

            new_business_urn = generate_urn('business')

            # create business
            new_business = Business(party_id=new_business_urn,
                                    business_ref=json["businessRef"],
                                    name=json["name"],
                                    trading_name=json["tradingName"],
                                    enterprise_name=json["enterpriseName"],
                                    contact_name=json["contactName"],
                                    address_line_1=json["addressLine1"],
                                    address_line_2=json["addressLine2"],
                                    address_line_3=json["addressLine3"],
                                    city=json["city"],
                                    postcode=json["postcode"],
                                    telephone=json["telephone"],
                                    employee_count=json["employeeCount"],
                                    facsimile=json["facsimile"],
                                    fulltime_count=json["fulltimeCount"],
                                    legal_status=json["legalStatus"],
                                    sic_2003=json["sic2003"],
                                    sic_2007=json["sic2007"],
                                    turnover=json["turnover"])

            db.session.add(new_business)
            db.session.flush()

            # commit the whole transaction
            db.session.commit()

        except:

            # rollback the whole transaction
            db.session.rollback()

            app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
            response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
            return response

        collection_path = response.headers["location"] = "/businesses/" + str(new_business.id)
        etag = hashlib.sha1(collection_path).hexdigest()
        response.set_etag(etag)

        response.headers["id"] = "/businesses/" + str(new_business.id)
        return response, 201

    return jsonify({"message": "Please provide a valid Json object.",
                    "hint": "you may need to pass a content-type: application/json header"}), 400


@app.route('/respondents/', methods=['POST'])
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

    app.logger.info("respondents/create_respondent()")

    # First check that we have a valid JWT token if we don't send a 400 error with authorisation failure
    if request.headers.get('authorization'):
        jwt_token = request.headers.get('authorization')
        if not validate_scope(jwt_token, 'ps.write'):
            res = Response(response="Invalid token/scope to access this Microservice Resource", status=400, mimetype="text/html")
            return res
    else:
        res = Response(response="Valid token/scope is required to access this Microservice Resource", status=400, mimetype="text/html")
        return res

    party_respondent = []

    json = request.json
    if json:
        response = make_response("")

        party_respondent.append(request.json)
        response.headers["location"] = "/respondents/"

        # Check that we have all the correct attributes in our json object.
        try:
            json["emailAddress"]
            json["firstName"]
            json["lastName"]
            json["telephone"]
            json["status"]
            json["enrolmentCode"]

        except KeyError:
            app.logger.warning("""Party Service POST did not contain correct mandatory
                               parameters in it's JSON payload: {}""".format(str(json)))
            res = Response(response="invalid input, object invalid", status=404, mimetype="text/html")
            return res

        if not validate_status_code(json["status"]):
            app.logger.warning("""Party Service POST did not contain a valid status code in the status field. We
                               received: {}""".format(json['status']))
            res = Response(response="invalid status code, object invalid", status=404, mimetype="text/html")
            return res

        if not validate_phone_number(json["telephone"]):
            app.logger.warning("""Party Service POST did not contain a valid UK phone number in the telephone field. We
                               received: {}""".format(json['telephone']))
            res = Response(response="invalid phone number, object invalid", status=404, mimetype="text/html")
            return res

        try:

            # generate a new respondent urn
            new_respondent_urn = generate_urn('respondent')

            # get the case context for the iac
            survey_id, business_id = get_case_context(json["enrolmentCode"])

            if survey_id and business_id:

                # set the statuses
                if json["status"] == 'CREATED':
                    business_association_status = 'INACTIVE'
                    enrolment_status = 'PENDING'
                elif json["status"] == 'ACTIVE':
                    business_association_status = 'ACTIVE'
                    enrolment_status = 'ACTIVE'
                elif json["status"] == 'SUSPENDED':
                    business_association_status = 'INACTIVE'
                    enrolment_status = 'SUSPENDED'
                else:
                    business_association_status = 'INACTIVE'
                    enrolment_status = 'PENDING'

                # create respondent
                new_respondent = Respondent(party_id=new_respondent_urn,
                                            status=json["status"],
                                            email_address=json["emailAddress"],
                                            first_name=json["firstName"],
                                            last_name=json["lastName"],
                                            telephone=json["telephone"])
                db.session.add(new_respondent)
                db.session.flush()

                # create business association
                new_business_association = BusinessAssociation(business_id=business_id,
                                                               respondent_id=new_respondent.id,
                                                               status=business_association_status)
                db.session.add(new_business_association)
                db.session.flush()

                # create enrolment
                new_enrolment = Enrolment(business_association_id=new_business_association.id,
                                          survey_id=survey_id,
                                          status=enrolment_status)
                db.session.add(new_enrolment)

                # create enrolment invitation
                verification_token = str(uuid.uuid4())
                sms_verification_token = randint(0, 999999)
                new_enrolment_invitation = EnrolmentInvitation(respondent_id=new_respondent.id,
                                                               target_email=json["emailAddress"],
                                                               verification_token=verification_token,
                                                               sms_verification_token=sms_verification_token,
                                                               status='ACTIVE')

                db.session.add(new_enrolment_invitation)

                # TODO call notification service to send verification email

                # commit the whole transaction
                db.session.commit()

            else:

                app.logger.info("Could not establish case context for iac: {}".format(json["enrolmentCode"]))
                response = Response(response="Case context could not be established", status=404, mimetype="text/html")
                return response

        except:

            # rollback the whole transaction
            db.session.rollback()

            app.logger.error("DB exception: {}".format(sys.exc_info()[0]))
            response = Response(response="Error in the Party DB.", status=500, mimetype="text/html")
            return response

        collection_path = response.headers["location"] = "/respondents/" + str(new_respondent.id)
        etag = hashlib.sha1(collection_path).hexdigest()
        response.set_etag(etag)

        response.headers["id"] = "/respondents/" + str(new_respondent.id)
        return response, 201

    return jsonify({"message": "Please provide a valid Json object.",
                    "hint": "you may need to pass a content-type: application/json header"}), 400


if __name__ == '__main__':
    # Create a file handler to handle our logging
    handler = RotatingFileHandler('application.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s ' '[in %(pathname)s:%(lineno)d]'))
    # Initialise SqlAlchemy configuration here to avoid circular dependency
    db.init_app(app)

    # Run
    PORT = int(os.environ.get('PORT', 5062))
    app.run(host='0.0.0.0', port=PORT, debug=False)
