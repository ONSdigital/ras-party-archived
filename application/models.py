"""
This module contains the data model for the collection instrument
"""

import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import TEXT, JSON, UUID

from app import db


class Respondent(db.Model):

    __tablename__ = 'ras_respondents'
    __table_args__ = {"schema": "ras_party"}
    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(TEXT)
    status = db.Column(TEXT)
    email_address = db.Column(TEXT)
    first_name = db.Column(TEXT)
    last_name = db.Column(TEXT)
    telephone = db.Column(TEXT)
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, party_id, status, email_address, first_name, last_name, telephone, id=None):
        self.id = id
        self.party_id = party_id
        self.status = status
        self.email_address = email_address
        self.first_name = first_name
        self.last_name = last_name
        self.telephone = telephone


class BusinessAssociation(db.Model):

    __tablename__ = 'ras_business_associations'
    __table_args__ = {"schema": "ras_party"}
    id = db.Column(db.Integer, primary_key=True)
    business_id = db.Column(db.INTEGER)
    respondent_id = db.Column(db.INTEGER)
    status = db.Column(TEXT)
    effective_from = db.Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = db.Column(DateTime)
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, business_id, respondent_id, status, effective_from=None, effective_to=None, id=None):
        self.id = id
        self.business_id = business_id
        self.respondent_id = respondent_id
        self.status = status
        self.effective_from = effective_from
        self.effective_to= effective_to


class Enrolment(db.Model):

    __tablename__ = 'ras_enrolments'
    __table_args__ = {"schema": "ras_party"}
    id = db.Column(db.Integer, primary_key=True)
    business_association_id = db.Column(db.INTEGER)
    survey_id = db.Column(TEXT)
    status = db.Column(TEXT)
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, business_association_id, survey_id, status, id=None):
        self.id = id
        self.business_association_id = business_association_id
        self.survey_id = survey_id
        self.status = status


class Business(db.Model):

    __tablename__ = 'ras_businesses'
    __table_args__ = {"schema": "ras_party"}
    id = db.Column(db.Integer, primary_key=True)
    business_ref = db.Column(TEXT)
    party_id = db.Column(TEXT)
    name = db.Column(TEXT)
    trading_name = db.Column(TEXT)
    enterprise_name = db.Column(TEXT)
    contact_name = db.Column(TEXT)
    address_line_1 = db.Column(TEXT)
    address_line_2 = db.Column(TEXT)
    address_line_3 = db.Column(TEXT)
    city = db.Column(TEXT)
    postcode = db.Column(TEXT)
    telephone = db.Column(TEXT)
    employee_count = db.Column(db.INTEGER)
    facsimile = db.Column(TEXT)
    fulltime_count = db.Column(db.INTEGER)
    legal_status = db.Column(TEXT)
    sic_2003 = db.Column(TEXT)
    sic_2007 = db.Column(TEXT)
    turnover = db.Column(db.INTEGER)
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, business_ref, party_id, name, trading_name, enterprise_name,
                 contact_name, address_line_1, address_line_2, address_line_3, city,
                 postcode, telephone,    employee_count, facsimile, fulltime_count,
                 legal_status, sic_2003, sic_2007, turnover, id=None):
        self.id = id
        self.business_ref = business_ref
        self.party_id = party_id
        self.name = name
        self.trading_name = trading_name
        self.enterprise_name = enterprise_name
        self.contact_name = contact_name
        self.address_line_1 = address_line_1
        self.address_line_2 = address_line_2
        self.address_line_3 = address_line_3
        self.city = city
        self.postcode = postcode
        self.telephone = telephone
        self.employee_count = employee_count
        self.facsimile = facsimile
        self.fulltime_count = fulltime_count
        self.legal_status = legal_status
        self.sic_2003 = sic_2003
        self.sic_2007 = sic_2007
        self.turnover = turnover


class EnrolmentCode(db.Model):

    __tablename__ = 'ras_enrolment_codes'
    __table_args__ = {"schema": "ras_party"}
    id = db.Column(db.Integer, primary_key=True)
    respondent_id = db.Column(db.INTEGER)
    business_id = db.Column(db.INTEGER)
    survey_id = db.Column(TEXT)
    iac = db.Column(TEXT)
    status = db.Column(TEXT)
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, respondent_id, business_id, survey_id, iac, status, id=None):
        self.id = id
        self.respondent_id = respondent_id
        self.business_id = business_id
        self.survey_id = survey_id
        self.status = status
        self.iac = iac


class EnrolmentInvitation(db.Model):

    __tablename__ = 'ras_enrolment_invitations'
    __table_args__ = {"schema": "ras_party"}
    id = db.Column(db.Integer, primary_key=True)
    respondent_id = db.Column(db.INTEGER)
    business_id = db.Column(db.INTEGER)
    survey_id = db.Column(TEXT)
    target_email = db.Column(TEXT)
    verification_token = db.Column(UUID)
    sms_verification_token = db.Column(db.INTEGER)
    effective_from = db.Column(DateTime, default=datetime.datetime.utcnow)
    effective_to = db.Column(DateTime, default=datetime.datetime.utcnow()+datetime.timedelta(days=2))
    status = db.Column(TEXT)
    created_on = db.Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, respondent_id, business_id, survey_id, target_email,
                 verification_token, sms_verification_token, status, id=None):
        self.id = id
        self.respondent_id = respondent_id
        self.business_id = business_id
        self.survey_id = survey_id
        self.target_email = target_email
        self.verification_token = verification_token
        self.sms_verification_token = sms_verification_token
        self.status = status
