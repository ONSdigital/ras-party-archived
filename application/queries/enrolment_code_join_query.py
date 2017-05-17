from application.database import db
from application.models import Business, EnrolmentCode


class EnrolmentCodeBusinessJoinQuery:

    def __init__(self, filters):
        self.filters = filters

    def query(self):
        return (db.session.query(EnrolmentCode, Business)
                .filter(EnrolmentCode.business_id == Business.id, *self.filters))
