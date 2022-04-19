##################################################################### SetupApp ###################################################################
import os
import pathlib
from flask_login import current_user

import requests
from flask import Flask, session, abort, redirect, request,render_template
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask("Google Login App")
app.secret_key = "CodeSpecialist.com"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "821661327953-jva1j149g2arqrsrovq1hum65tp9eui4.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)

##################################################################### SetupApp ###################################################################


##################################################################### Setup mySQL ################################################################




##################################################################### Setup mySQL ################################################################                                                         




                                                                ### Login ###

def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper


@app.route("/Glogin")
def Glogin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/auth_home",session['name'])


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
                                                                ### Login ###




                                                                ### RenderTemplate ###


@app.route("/")
def home():
    return render_template('home.html')

@app.route("/enroll")
def enroll():
    return render_template('enroll.html')

@app.route("/profile")
def profile():
    return render_template('profile.html')

@app.route("/login")
def login():
    return render_template('login.html')

@app.route("/auth_home")
@login_is_required
def auth_home():
    return render_template('auth_home.html')


                                                                ### RenderTemplate ###



                                                                ### RunApp ###

if __name__ == "__main__":
    app.run(debug=True)

                                                                ### RunApp ###    