from application.models import Business


class BusinessQuery:

    def __init__(self, filters):
        self.filters = filters

    def query(self):
        return Business.query.filter(*self.filters)
