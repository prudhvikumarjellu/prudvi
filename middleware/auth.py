import json

from flask import request
import jwt

import config
from common import strings
from common.blueprint import Blueprint
from common.response import success, failure
from common.utils.time_utils import get_auth_exp

auth_api_v1 = Blueprint('auth', __name__, url_postfix='auth')


class AuthMiddleware(object):

    def __init__(self, app):
        self.app = app
        sample_jwt()

    def __call__(self, environ, start_response):
        path = str(environ['PATH_INFO'])
        token = environ.get('HTTP_AUTHORIZATION', None)

        if not config.ENABLE_AUTH:
            print("authentication skipped")
            return self.app(environ, start_response)

        if path.__contains__('/signup') or path.__contains__('/signin') or path.__contains__('/get-token'):
            print("authentication skipped")
            return self.app(environ, start_response)

        if not token:
            return self.token_missing(environ, start_response)

        token_validation = self.authenticated(token)

        print(token_validation)

        if not token_validation[0]:
            return self.token_expired(environ, start_response)

        if token_validation[1]:
            return self.app(environ, start_response)
        else:
            return self.token_missing(environ, start_response)

    @staticmethod
    def authenticated(token):
        try:

            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.JWT_ALGORITHM])

            print(payload)

            # todo replace with get users by id and email
            is_authorised = check_valid_user(payload)
            print("IS_AUTHORISED", is_authorised)
            return True, is_authorised
        except Exception as err:
            print(err)
            return False, None

    @staticmethod
    def token_missing(environ, start_response):
        start_response('401 Unauthorized', [('Content-Type', 'text/html')])
        return [b'Unauthorized']

    @staticmethod
    def token_expired(environ, start_response):
        start_response('419 Authentication Timeout', [('Content-Type', 'text/html')])
        return [b'Authentication Timeout']


def get_jwt(_id, api_key):
    try:
        identity = {'identity': _id, 'api_key': api_key, "exp": get_auth_exp(config.JWT_TOKEN_TIME_OUT_IN_MINUTES)}
        token = jwt.encode(identity, config.SECRET_KEY, config.JWT_ALGORITHM)
        return token.decode("utf-8")
    except Exception as err:
        print("get_jwt", err)
        return None


def check_valid_user(payload):
    try:
        obj = get_user_by_id(payload['identity'])

        print("----------------------", obj)

        if not obj:
            return False

        return payload['api_key'] is not None
    except Exception as err:
        print("check_valid_user", str(err))
        return False


@auth_api_v1.route('/get-token', methods=['POST'])
def get_token():
    try:
        data = json.loads(request.data.decode('utf-8'))

        _id = data.get('uid', None)
        api_key = data.get('api_key', 'DEFAULT')

        payload = {'identity': _id, 'api_key': api_key}

        if not check_valid_user(payload):
            return failure(strings.invalid_credentials)

        token = get_jwt(_id, api_key)

        if token:
            token = {'token': str(token)}
            return success(strings.retrieved_success, token)
        else:
            return failure(strings.verification_failed)

    except Exception as e:
        print("get_token", e)
        return failure(str(e))


def sample_jwt():
    actual = {'uid': '1', 'api_key': 'api-secret-key',
              'exp': get_auth_exp(config.JWT_TOKEN_TIME_OUT_IN_MINUTES)}
    token = get_jwt(actual['uid'], actual['api_key'])
    return token


def get_user_by_id(_id):
    try:
        # Don't remove from here
        from api.user.models import User

        obj = User.query.get(_id)._asdict()
        print(obj)
        return obj
    except Exception as err:
        print("get_user_by_id - ", str(err))
        return None
