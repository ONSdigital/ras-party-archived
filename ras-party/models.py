"""
This module contains the data model for the collection instrument
"""

import datetime

from sqlalchemy import DateTime
from sqlalchemy.dialects.postgresql import TEXT, JSON, UUID

from app import db


class Respondent(db.Model):
    """
    The respondent model
    """
    __tablename__ = 'ras_respondents'
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
