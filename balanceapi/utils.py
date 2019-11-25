import typing
from functools import wraps

import flask
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery


def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }


def login_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if "credentials" not in flask.session:
            return flask.redirect("authorize")
        return func(*args, **kwargs)

    return decorated


def get_sheet():
    credentials = google.oauth2.credentials.Credentials(**flask.session["credentials"])
    flask.session["credentials"] = credentials_to_dict(credentials)
    service = googleapiclient.discovery.build("sheets", "v4", credentials=credentials)
    sheet = service.spreadsheets()
    return sheet


def get_data_from_sheet(**kwargs) -> typing.List[typing.Tuple[str]]:
    request = get_sheet().values().get(**kwargs)
    response = request.execute()
    return response.get("values", [])
