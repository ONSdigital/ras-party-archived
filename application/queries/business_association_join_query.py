from application.database import db
from application.models import Business, BusinessAssociation, Respondent, Enrolment


class BusinessAssociationJoinQuery:

    def __init__(self, filters):
        self.filters = filters

    def query(self):
        return (db.session.query(Business, BusinessAssociation, Respondent, Enrolment)
                .filter(Business.id == BusinessAssociation.business_id,
                BusinessAssociation.respondent_id == Respondent.id,
                BusinessAssociation.id == Enrolment.business_association_id,
                *self.filters))
