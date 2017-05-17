from validator import Validator
import logging
import phonenumbers
from phonenumbers.phonenumberutil import NumberParseException


class PhoneNumber(Validator):
    def __init__(self, json):
        super(PhoneNumber, self).__init__(json)

    def is_valid(self):

        if not self._json.get('telephone'):
            return False

        telephone = self._json.get('telephone')

        if len(telephone) > 16:
            return False
        try:
            logging.info("Checking this is a valid GB Number")
            input_number = phonenumbers.parse(telephone, "GB")

            if not (phonenumbers.is_possible_number(input_number)):
                return False

            if not (phonenumbers.is_valid_number(input_number)):
                return False
        except NumberParseException:
            logging.info("There is a number parse exception in the phonenumber field")
            return False

        return True

    @staticmethod
    def get_message():
        return "Party Service POST did not contain a valid UK phone number in the telephone field"
