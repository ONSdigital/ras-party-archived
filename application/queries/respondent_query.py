from application.models import Respondent


class RespondentQuery:

    def __init__(self, filters):
        self.filters = filters

    def query(self):
        return Respondent.query.filter(*self.filters)
