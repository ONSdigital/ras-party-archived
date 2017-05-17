from application import settings
from validator import Validator


class LegalStatus(Validator):
    def __init__(self, json):
        super(LegalStatus, self).__init__(json)

    def is_valid(self):

        if self._json.get('legalStatus') and self._json['legalStatus'] in settings.LEGAL_STATUS_CODES:
            return True
        else:
            return False

    @staticmethod
    def get_message():
        return "Party Service POST did not contain a valid legal status code in the legal status field"
