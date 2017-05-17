"""
Util module
"""

from random import randint

from authentication.jwt import decode


def get_jwt_from_header(auth_header_value):
    """
    returns jwt token out of the auth header
    """
    jwt_dict = decode(auth_header_value)
    return jwt_dict


def generate_urn(id_type):
    sequence = randint(0, 99999999999)
    urn = "urn:ons.gov.uk:id:" + id_type + ":" + str(sequence)
    return urn
