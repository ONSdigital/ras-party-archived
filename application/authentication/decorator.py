from functools import wraps
from flask import request, Response
from application.authentication.validate_scope import validate_scope


def authorization_required(scope):
    """
        If you decorate a view with this, it will ensure that the jwt has
        the correct scope before calling the view.
        :param scope: The scope required by the function being decorated
    """

    def authorization_required_decorator(func):
        @wraps(func)
        def authorization_required_wrapper(*args, **kwargs):
            if request.headers.get('authorization'):
                jwt_token = request.headers.get('authorization')
                if validate_scope(jwt_token, scope):
                    return func(*args, **kwargs)
            return Response(response="Access forbidden", status=403, mimetype="text/html")
        return authorization_required_wrapper
    return authorization_required_decorator
