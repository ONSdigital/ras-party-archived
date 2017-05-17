from validator import RequiredKeysValidator


class RequiredKeys(RequiredKeysValidator):
    def __init__(self, required_keys, json):
        super(RequiredKeys, self).__init__(required_keys, json)

    def is_valid(self):
            for key in self._required_keys:
                if key in self._json:
                    return True
                else:
                    return False

    @staticmethod
    def get_message():
        return "A required key is missing from the JSON"
