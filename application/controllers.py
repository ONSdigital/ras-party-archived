import hashlib
import logging
import sys
import uuid
from json import JSONEncoder
from random import randint

from queries.business_association_join_query import BusinessAssociationJoinQuery
from queries.business_query import BusinessQuery
from queries.enrolment_code_join_query import EnrolmentCodeBusinessJoinQuery
from queries.respondent_query import RespondentQuery
from flask import Response
from sqlalchemy import exc

import settings
from database import db
from models import Respondent, BusinessAssociation, Enrolment, Business, EnrolmentCode, EnrolmentInvitation
from utils import generate_urn
from exception import DBError


def get_enrolment_code_response(enrolment_code):

    filters = (EnrolmentCode.respondent_id.is_(None),
               EnrolmentCode.status == "ACTIVE",
               EnrolmentCode.iac == enrolment_code)

    enrolment_code_query = EnrolmentCodeBusinessJoinQuery(filters)
    enrolment_code_results = _execute_query(enrolment_code_query)

    enrolment_details = [{
                    'surveyId': enc.survey_id,
                    'businessId': bus.party_id,
                    'businessRef': bus.business_ref,
                    'businessName': bus.name,
                    'IACStatus': enc.status} for enc, bus in enrolment_code_results]

    return _build_response(enrolment_details, settings.RAS_ENROLEMENT_CODE_NOT_FOUND)


def get_business_by_ref_response(business_ref):

    filters = (Business.business_ref == business_ref,)

    business_by_ref_query = BusinessQuery(filters)
    business_by_ref_results = _execute_query(business_by_ref_query)

    business_details = [{
        'businessRef': rec.business_ref,
        'businessId': rec.party_id,
        'businessName': rec.name,
        'businessTradingName': rec.trading_name,
        'businessEnterpriseName': rec.enterprise_name,
        'businessContactName': rec.contact_name,
        'addressLine1': rec.address_line_1,
        'addressLine2': rec.address_line_2,
        'addressLine3': rec.address_line_3,
        'city': rec.city,
        'postcode': rec.postcode,
        'telephone': rec.telephone,
        'facsimile': rec.facsimile,
        'employeeCount': rec.employee_count,
        'fulltimeCount': rec.fulltime_count,
        'legaStatus': rec.legal_status,
        'sic2003': rec.sic_2003,
        'sic2007': rec.sic_2007,
        'turnover': rec.turnover}
        for rec in business_by_ref_results]

    return _build_response(business_details, settings.RAS_BUSINESS_NOT_FOUND)


def get_business_associations_by_business_id_response(business_id):

    filters = (Business.party_id == business_id,)
    business_associations_query = BusinessAssociationJoinQuery(filters)
    business_associations_result = _execute_query(business_associations_query)

    business_details = [{
                            'businessRef': bus.business_ref,
                            'businessId': bus.party_id,
                            'businessName': bus.name,
                            'businessStatus': bua.status,
                            'respondentEmailAddress': res.email_address,
                            'respondentFirstName': res.first_name,
                            'respondentLastName': res.last_name,
                            'surveyId': enr.survey_id}
                        for bus, bua, res, enr in business_associations_result]
    return _build_response(business_details, settings.RAS_BUSINESS_ASSOCIATION_NOT_FOUND)


def get_business_associations_by_respondent_id_response(respondent_id):

    filters = (Respondent.party_id == respondent_id,)
    business_associations_query = BusinessAssociationJoinQuery(filters)
    business_associations_query_result = _execute_query(business_associations_query)

    business_details = [{
                            'businessRef': bus.business_ref,
                            'businessId': bus.party_id,
                            'businessName': bus.name,
                            'businessStatus': bua.status,
                            'respondentEmailAddress': res.email_address,
                            'respondentFirstName': res.first_name,
                            'respondentLastName': res.last_name,
                            'surveyId': enr.survey_id}
                        for bus, bua, res, enr in business_associations_query_result]

    return _build_response(business_details, settings.RAS_BUSINESS_ASSOCIATION_NOT_FOUND)


def get_business_by_id_response(business_id):

    filters = (Business.party_id == business_id,)
    business_query = BusinessQuery(filters)
    business_query_result = _execute_query(business_query)
    business_details = [{
        'businessRef': rec.business_ref,
        'businessId': rec.party_id,
        'businessName': rec.name,
        'businessTradingName': rec.trading_name,
        'businessEnterpriseName': rec.enterprise_name,
        'businessContactName': rec.contact_name,
        'addressLine1': rec.address_line_1,
        'addressLine2': rec.address_line_2,
        'addressLine3': rec.address_line_3,
        'city': rec.city,
        'postcode': rec.postcode,
        'telephone': rec.telephone,
        'facsimile': rec.facsimile,
        'employeeCount': rec.employee_count,
        'fulltimeCount': rec.fulltime_count,
        'legaStatus': rec.legal_status,
        'sic2003': rec.sic_2003,
        'sic2007': rec.sic_2007,
        'turnover': rec.turnover}
        for rec in business_query_result]

    return _build_response(business_details, settings.RAS_BUSINESS_NOT_FOUND)


def get_case_context(enrolment_code):
    survey_id = None
    business_id = None

    filters = (EnrolmentCode.iac == enrolment_code,)

    enrolment_code_query = EnrolmentCodeBusinessJoinQuery(filters)
    enrolment_code_results = _execute_query(enrolment_code_query)
    enrolment_details = [[enc.survey_id, bus.id] for enc, bus in enrolment_code_results]

    if enrolment_details:
        survey_id = enrolment_details[0][0]
        business_id = enrolment_details[0][1]

    return survey_id, business_id


def get_respondent(enrolment_invitation):

    filters = (Respondent.id == enrolment_invitation.respondent_id,)
    respondent_query = RespondentQuery(filters)
    respondent_query_results = _execute_query(respondent_query)

    existing_respondent = [[res.id, res.party_id, res.email_address,
                            res.first_name, res.last_name, res.telephone]
                           for res in respondent_query_results]
    return existing_respondent


def get_business_associate(enrolment_invitation, respondent):

    business_association = (db.session.query(BusinessAssociation)
                            # .filter(BusinessAssociation.status == 'PENDING')
                            .filter(BusinessAssociation.respondent_id == respondent.id)
                            .filter(BusinessAssociation.business_id == enrolment_invitation.business_id))

    existing_business_association = [[bua.id, bua.business_id, bua.respondent_id,
                                      bua.effective_from, bua.effective_to]
                                     for bua in business_association]
    return existing_business_association


def get_enrolment(business_association, enrolment_invitation):

    enrolment = (db.session.query(Enrolment)
                 # .filter(Enrolment.status == 'PENDING')
                 .filter(Enrolment.business_association_id == business_association.id)
                 .filter(Enrolment.survey_id == enrolment_invitation.survey_id))

    existing_enrolment = [[enr.id, enr.business_association_id, enr.survey_id] for enr in enrolment]
    return existing_enrolment


def get_enrolment_invitation(verification_token, status):

    enrolment_invitation = (db.session.query(EnrolmentInvitation)
                            .filter(EnrolmentInvitation.status == status)
                            .filter(EnrolmentInvitation.verification_token == verification_token))

    existing_enrolment_invitation = [[eni.id, eni.respondent_id, eni.business_id, eni.survey_id,
                                      eni.target_email, eni.verification_token,
                                      eni.sms_verification_token, eni.status]
                                     for eni in enrolment_invitation]

    return existing_enrolment_invitation


def create_business(json, response):

    business_urn = generate_urn('business')
    business_ref = json.get("businessRef")
    name = json.get("name")
    trading_name = json.get("tradingName")
    enterprise_name = json.get("enterpriseName")
    contact_name = json.get("contactName")
    address_line_1 = json.get("addressLine1")
    address_line_2 = json.get("addressLine2")
    address_line_3 = json.get("addressLine3")
    city = json.get("city")
    postcode = json.get("postcode")
    telephone = json.get("telephone")
    employee_count = json.get("employeeCount")
    facsimile = json.get("facsimile")
    full_time_count = json.get("fulltimeCount")
    legal_status = json.get("legalStatus")
    sic_2003 = json.get("sic2003")
    sic_2007 = json.get("sic2007")
    turnover = json.get("turnover")

    business = Business(party_id=business_urn,
                        business_ref=business_ref,
                        name=name,
                        trading_name=trading_name,
                        enterprise_name=enterprise_name,
                        contact_name=contact_name,
                        address_line_1=address_line_1,
                        address_line_2=address_line_2,
                        address_line_3=address_line_3,
                        city=city,
                        postcode=postcode,
                        telephone=telephone,
                        employee_count=employee_count,
                        facsimile=facsimile,
                        fulltime_count=full_time_count,
                        legal_status=legal_status,
                        sic_2003=sic_2003,
                        sic_2007=sic_2007,
                        turnover=turnover)

    try:
        db.session.add(business)
        db.session.flush()
        db.session.commit()

    except:
        db.session.rollback()
        logging.error("DB exception: {}".format(sys.exc_info()[0]))
        return Response(response=settings.RAS_DB_ERROR, status=500, mimetype="text/html")

    collection_path = response.headers["location"] = "/businesses/" + str(business.id)
    etag = hashlib.sha1(collection_path).hexdigest()
    response.set_etag(etag)
    response.headers["id"] = "/businesses/"

    return response


def create_respondent_db(json, response):

    try:
        # generate a new respondent urn
        respondent_urn = generate_urn('respondent')

        # get the case context for the iac

        survey_id, business_id = get_case_context(json["enrolmentCode"])

        if survey_id and business_id:
            business_association_status = 'PENDING'
            enrolment_status = 'PENDING'
            status = json.get("status")
            email_address = json.get("emailAddress")
            first_name = json.get("firstName")
            last_name = json.get("lastName")
            telephone = json.get("telephone")
            respondent = Respondent(party_id=respondent_urn,
                                    status=status,
                                    email_address=email_address,
                                    first_name=first_name,
                                    last_name=last_name,
                                    telephone=telephone)
            db.session.add(respondent)
            db.session.flush()

            # create business association
            business_association = BusinessAssociation(business_id=business_id,
                                                       respondent_id=respondent.id,
                                                       status=business_association_status)
            db.session.add(business_association)
            db.session.flush()
            # create enrolment
            enrolment = Enrolment(business_association_id=business_association.id,
                                  survey_id=survey_id,
                                  status=enrolment_status)
            db.session.add(enrolment)

            # create enrolment invitation
            verification_token = str(uuid.uuid4())
            sms_verification_token = randint(0, 999999)
            enrolment_invitation = EnrolmentInvitation(respondent_id=respondent.id,
                                                       business_id=business_id,
                                                       survey_id=survey_id,
                                                       target_email=email_address,
                                                       verification_token=verification_token,
                                                       sms_verification_token=sms_verification_token,
                                                       status='ACTIVE')

            db.session.add(enrolment_invitation)
            db.session.commit()

        else:

            logging.info("Could not establish case context for iac: {}".format(json["enrolmentCode"]))
            response = Response(response="Case context could not be established", status=404, mimetype="text/html")

    except:
        db.session.rollback()

    collection_path = response.headers["location"] = "/respondents/" + str(respondent.id)
    etag = hashlib.sha1(collection_path).hexdigest()
    response = Response(response="", status=200, mimetype="collection+json")
    response.set_etag(etag)
    response.headers["id"] = "/respondents/" + str(respondent.id)
    return response


def set_verification_token_as_redeemed_from_db(verification_token):

    try:
        # redeem the verification token
        existing_enrolment_invitation = get_enrolment_invitation(verification_token, 'ACTIVE')

        if not existing_enrolment_invitation:
            logging.info("Verification token not found for set_verification_token_as_redeemed")
            response = Response(response="Verification token not found", status=404, mimetype="text/html")
            return response

        enrolment_invitation = EnrolmentInvitation(id=existing_enrolment_invitation[0][0],
                                                   respondent_id=existing_enrolment_invitation[0][1],
                                                   business_id=existing_enrolment_invitation[0][2],
                                                   survey_id=existing_enrolment_invitation[0][3],
                                                   target_email=existing_enrolment_invitation[0][4],
                                                   verification_token=existing_enrolment_invitation[0][5],
                                                   sms_verification_token=existing_enrolment_invitation[0][6],
                                                   status='REDEEMED')

        db.session.merge(enrolment_invitation)
        db.session.flush()

        # activate the respondent
        existing_respondent = get_respondent(enrolment_invitation)

        if not existing_respondent:
            response = _roll_back_db(existing_respondent)
            return response

        respondent = Respondent(id=existing_respondent[0][0],
                                party_id=existing_respondent[0][1],
                                status='ACTIVE',
                                email_address=existing_respondent[0][2],
                                first_name=existing_respondent[0][3],
                                last_name=existing_respondent[0][4],
                                telephone=existing_respondent[0][5])
        db.session.merge(respondent)
        db.session.flush()

        existing_business_association = get_business_associate(enrolment_invitation, respondent)

        if not existing_business_association:
            response = _roll_back_db()
            return response

        business_association = BusinessAssociation(id=existing_business_association[0][0],
                                                   business_id=existing_business_association[0][1],
                                                   respondent_id=existing_business_association[0][2],
                                                   status='ACTIVE',
                                                   effective_from=existing_business_association[0][3],
                                                   effective_to=existing_business_association[0][4])
        db.session.merge(business_association)
        db.session.flush()

        existing_enrolment = get_enrolment(business_association, enrolment_invitation)

        if not existing_enrolment:
            response = _roll_back_db()
            return response

        enrolment = Enrolment(id=existing_enrolment[0][0],
                              business_association_id=existing_enrolment[0][1],
                              survey_id=existing_enrolment[0][2],
                              status='ENABLED')
        db.session.merge(enrolment)
        db.session.commit()

    except exc.OperationalError:
        db.session.rollback()
        # return _db_exception()

    response = Response(response="Verification token redeemed", status=200, mimetype="text/html")
    return response


def set_enrolment_code_as_redeemed_from_db(enrolment_code, respondent_urn):

    try:
        enrolment_codes = (db.session.query(EnrolmentCode)
                           .filter(EnrolmentCode.status == 'ACTIVE')
                           .filter(EnrolmentCode.iac == enrolment_code))

        existing_enrolment_code = [[enc.id, enc.business_id, enc.survey_id, enc.iac, enc.status]
                                   for enc in enrolment_codes]

        if not existing_enrolment_code:
            logging.info("Enrolment code not found for set_enrolment_code_as_redeemed")
            response = Response(response="Enrolment code not found", status=404, mimetype="text/html")
            return response

        respondents = (db.session.query(Respondent).filter(Respondent.party_id == respondent_urn))
        respondent_id = [[res.id] for res in respondents]

        if not respondent_id:
            logging.info("Respondent not found for set_enrolment_code_as_redeemed")
            response = Response(response="Respondent not found", status=404, mimetype="text/html")
            return response

        enrolment_code = EnrolmentCode(id=existing_enrolment_code[0][0],
                                       respondent_id=respondent_id[0][0],
                                       business_id=existing_enrolment_code[0][1],
                                       survey_id=existing_enrolment_code[0][2],
                                       iac=existing_enrolment_code[0][3],
                                       status='REDEEMED')

        db.session.merge(enrolment_code)
        db.session.commit()

    except exc.OperationalError:
        return "Db error"

    response = Response(response="Enrolment code redeemed", status=200, mimetype="text/html")
    return response


def _roll_back_db():
    db.session.rollback()
    logging.info("Record not found, rolling back db")
    response = Response(response="Record not found, rolling back db", status=404, mimetype="text/html")
    return response


def _encode_dict(query_result):
    encoded_results = JSONEncoder().encode(query_result)
    return Response(response=encoded_results, status=200, mimetype="collection+json")


def _build_response(results_dict, not_found_message):
    if results_dict:
        response = _encode_dict(results_dict)
    else:
        logging.info("{}".format(not_found_message))
        response = Response(response=not_found_message, status=404, mimetype="text/html")
    return response


def _execute_query(query_class):
    try:
        return query_class.query()
    except exc.OperationalError:
        logging.error("DB exception: {}".format(sys.exc_info()[0]))
        raise DBError(settings.RAS_DB_ERROR, status_code=400)
