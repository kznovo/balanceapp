import datetime
import os
import configparser

import flask
import requests
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

from balanceapi.utils import (
    credentials_to_dict,
    login_required,
    get_sheet,
    get_data_from_sheet,
)

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

cfg = configparser.ConfigParser()
cfg.read("config.ini")

app = flask.Flask(__name__)
flask_secret_file = cfg.get("Credentials", "flask_secret_file")
with open(flask_secret_file) as f:
    app.secret_key = f.read().strip()


@app.route("/")
@login_required
def index():
    spreadsheet_id = cfg.get("Spreadsheet", "spreadsheet_id")
    range_ = cfg.get("Spreadsheet", "expense_range")
    expense_data = get_data_from_sheet(spreadsheetId=spreadsheet_id, range=range_, majorDimension="COLUMNS")
    total_expense = sum(map(int, expense_data[1]))
    return flask.render_template("index.html", total_expense=total_expense)


def post(db="income", **kwargs):
    spreadsheet_id = cfg.get("Spreadsheet", "spreadsheet_id")
    range_ = cfg.get("Spreadsheet", db + "_range")
    value_input_option = "RAW"
    insert_data_option = "OVERWRITE"
    columns = cfg.get("Spreadsheet", db + "_columns").split(",")
    values = [kwargs.get(c, "") for c in columns]
    value_range_body = {"values": [values]}
    request = (
        get_sheet()
        .values()
        .append(
            spreadsheetId=spreadsheet_id,
            range=range_,
            valueInputOption=value_input_option,
            insertDataOption=insert_data_option,
            body=value_range_body,
        )
    )
    request.execute()


@app.route("/db/<db>", methods=["GET", "POST"])
@login_required
def income(db):
    if flask.request.method == "POST":
        timestamp = datetime.datetime.now().strftime("%m/%d/%Y%H:%M:%S")
        post(db, timestamp=timestamp, **flask.request.form)
        return 'Success!<br><a href="/">return</a>'
    else:
        spreadsheet_id = cfg.get("Spreadsheet", "spreadsheet_id")
        range_ = cfg.get("Spreadsheet", db + "_range")
        data = get_data_from_sheet(spreadsheetId=spreadsheet_id, range=range_)
        return flask.jsonify(data)


@app.route("/oauth2callback")
def oauth2callback():
    client_secrets_file = cfg.get("Credentials", "client_secrets_file")
    scopes = cfg.get("Spreadsheet", "scopes").split(",")
    state = flask.session["state"]
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file, scopes=scopes, state=state,
    )
    flow.redirect_uri = flask.url_for("oauth2callback", _external=True)
    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    flask.session["credentials"] = credentials_to_dict(credentials)
    return flask.redirect(flask.url_for("index"))


@app.route("/authorize")
def authorize():
    client_secrets_file = cfg.get("Credentials", "client_secrets_file")
    scopes = cfg.get("Spreadsheet", "scopes").split(",")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        client_secrets_file=client_secrets_file, scopes=scopes
    )
    flow.redirect_uri = flask.url_for("oauth2callback", _external=True)
    authorization_url, state = flow.authorization_url(
        access_type="offline", include_granted_scopes="true"
    )
    flask.session["state"] = state
    return flask.redirect(authorization_url)


@app.route("/revoke")
def revoke():
    if "credentials" not in flask.session:
        return (
            'You need to <a href="/authorize">authorize</a> before '
            + "testing the code to revoke credentials."
        )

    credentials = google.oauth2.credentials.Credentials(**flask.session["credentials"])

    revoke = requests.post(
        "https://accounts.google.com/o/oauth2/revoke",
        params={"token": credentials.token},
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    status_code = getattr(revoke, "status_code")
    if status_code == 200:
        return "Credentials successfully revoked."
    else:
        return "An error occurred."


@app.route("/clear")
def clear_credentials():
    if "credentials" in flask.session:
        del flask.session["credentials"]
    return "Credentials have been cleared.<br><br>"
