from contextlib import wraps
from datetime import datetime

from flask import Blueprint, abort, jsonify, request
from flask_login import current_user

from ..dao import (AlreadyUpToDate, check_api_key, get_homework_ordered,
                   get_messages)

api = Blueprint("api", __name__)

def api_auth(fn):
    """
    decorator
    Used to make sure that the api key
    or user cookie is used to use api
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        if not current_user.is_anonymous:
            # allow cookie auth
            return fn(*args, **kwargs)
        elif check_api_key(request.headers.get("x-api-key", default="", type=str)):
            # allow api-key sent in request header
            return fn(*args, **kwargs)
        else:
            return abort(401)
    return wrap

def api_date_checks(fn):
    """
    decorator that returns json for the date
    """
    @wraps(fn)
    def wrap(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except AlreadyUpToDate:
            return jsonify({"error": "AlreadyUpToDate", "loaded_data":tuple()})
        except ValueError:
            return jsonify({"error":"datetime not in correct format of YYYY/MM/DD H:M:S.MS"})
    return wrap

@api.route("/hwm/hw")
@api_auth
@api_date_checks
def hw():
    loaded_hw = get_homework_ordered(last_updated = request.args.get("last-update"))
    return jsonify(loaded_data=[hw.serialize() for hw in loaded_hw])

@api.route("/messages")
@api_auth
@api_date_checks
def messages():
    loaded_messages = get_messages(last_updated = request.args.get("last-update"))
    return jsonify(loaded_data=[message.serialize() for message in loaded_messages])