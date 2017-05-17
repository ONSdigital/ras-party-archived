import logging

from jose import JWTError

from application.authentication.jwt import decode


def validate_scope(jwt_token, scope_type):
    """
    This function checks a jwt token for a required scope type.

    :param jwt_token: String
    :param scope_type: String
    :return: Boolean
    """

    logging.info("validate_scope jwt_token: {}, scope_type: {}".format(jwt_token, scope_type))

    # Make sure we can decrypt the token and it makes sense

    return_val = False
    try:
        decrypted_jwt_token = decode(jwt_token)
        if decrypted_jwt_token['scope']:
            for user_scope_list in decrypted_jwt_token['scope']:
                if user_scope_list == scope_type:
                    logging.debug('Valid JWT scope.')
                    return_val = True

        if not return_val:
            logging.warning('Invalid JWT scope.')
            return False

        if decrypted_jwt_token['expires_at']:
            # We have a time stamp so check this token has not expired
            print('Token: {} has a UTC time stamp of: {}'.format(decrypted_jwt_token['access_token'], decrypted_jwt_token['expires_at']))
        else:
            # We don't have a time stamp
            logging.warning('Token has expired for token Value: {}'.format(decrypted_jwt_token['access_token']))
            return False

        return return_val

    except JWTError:
        logging.warning('JWT scope could not be validated.')
        return False

    except KeyError:
        logging.warning('JWT scope could not be validated.')
        return False
