class Validator(object):

    def __init__(self, json):
        self._json = json

    @staticmethod
    def is_valid():
        return True

    @staticmethod
    def get_message():
        return ""


class RequiredKeysValidator(Validator):

    def __init__(self, required_keys, json):
        self._required_keys = required_keys
        self._json = json
