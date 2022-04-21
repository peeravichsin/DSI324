##################################################################### SetupApp ###################################################################

import os
import pathlib
from datetime import datetime
from flask_login import current_user
from flask_mysqldb import MySQL
import requests
from flask import Flask, session, abort, redirect, request,render_template,flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask("EnrollCheck")
app.secret_key = "ifyouknowyouknowandifyoudontknowyoudontknow"


##################################################################### SetupApp ###################################################################


##################################################################### Setup mySQL ################################################################

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:soccer481200@localhost/dsi324'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'soccer481200'
app.config['MYSQL_DB'] = 'dsi324'
mysql = MySQL(app)

##################################################################### Setup mySQL ################################################################                                                         



##################################################################### Login ######################################################################


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "821661327953-jva1j149g2arqrsrovq1hum65tp9eui4.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)






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
    flash(f'Welcome { session["name"] }', category='success')
    return redirect("/auth_home")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

##################################################################### Login ######################################################################








##################################################################### FormFormat #################################################################


# Create Form
class TestFrom (FlaskForm):
    exam = StringField("Type something", validators=[DataRequired()])
    submit = SubmitField('Enter') 




##################################################################### FormFormat #################################################################










##################################################################### RenderTemplate #############################################################


# Default home
@app.route("/")
def home():
    return render_template('home.html')





# Enroll
@app.route("/enroll", methods =['GET','POST'])
def enroll():
    exam = None
    form = TestFrom()
    if form.validate_on_submit():
        exam = form.exam.data
        form.exam.data = ''
        flash("Submit Successfully!")
    return render_template('enroll.html',exam = exam, form = form)




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


##################################################################### RenderTemplate #############################################################







##################################################################### RunApp #####################################################################

if __name__ == "__main__":
    app.run(debug=True)

##################################################################### RunApp #####################################################################   