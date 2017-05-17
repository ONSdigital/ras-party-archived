from application import settings
from validator import Validator


class StatusCode(Validator):
    def __init__(self, json):
        super(StatusCode, self).__init__(json)

    def is_valid(self):
        if self._json["status"] in settings.STATUS_CODES:
            return True
        else:
            return False

    @staticmethod
    def get_message():
        return "Party Service POST did not contain a valid legal status code in the legal status field"
