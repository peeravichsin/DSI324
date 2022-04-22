##################################################################### SetupApp ###################################################################

import os
import pathlib
from datetime import datetime
from re import S
from unicodedata import name
from flask_mysqldb import MySQL
import requests
from flask import Flask, session, abort, redirect, request,render_template,flash,url_for
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

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'your password'
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
    session["email"] = id_info.get("email")
    cur = mysql.connection.cursor()
    user = cur.execute(f'SELECT * from Login WHERE user_id = {session["google_id"]}')
    if user:
        flash(f'Welcome { session["name"] }', category='success')
        return redirect("/auth_home")
    else:
        return redirect("/sign_up")
    
@app.route("/sign_up",methods =['GET','POST'])
def signup():
    if request.method == 'POST':
       user_id = session["google_id"]
       user_email = session["email"]
       student_email = session["email"]
       name = session["name"].split(' ')
       student_fname_en = name[0]
       student_lname_en = name[1]
       student_fname_th = request.form.get('student_fname_th')
       student_lname_th = request.form.get('student_lname_th')
       student_id = int(request.form.get('student_id'))
       faculty_id = 24
       major_name = request.form.get('major_name')
       cur = mysql.connection.cursor()
       cur.execute("INSERT INTO login (user_id, user_email) VALUES (%s, %s)", (user_id, user_email))
       mysql.connection.commit()
       cur.execute("INSERT INTO student (student_id, user_id, faculty_id, major_name, student_fname_en, student_lname_en, student_fname_th, student_lname_th, student_email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                           (student_id, user_id, faculty_id, major_name, student_fname_en, student_lname_en, student_fname_th, student_lname_th, student_email))
       mysql.connection.commit()
       cur.close()
       flash('Profile created!', category='success')
       return redirect(url_for('auth_home'))
    return render_template('sign_up.html')

@app.route("/logout")
@login_is_required
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
@login_is_required
@app.route("/enroll", methods =['GET','POST'])

def enroll():
    exam = None
    form = TestFrom()
    if form.validate_on_submit():
        exam = form.exam.data
        form.exam.data = ''
        flash("Submit Successfully!")
    return render_template('enroll.html',exam = exam, form = form)



@login_is_required
@app.route("/profile")

def profile():
    return render_template('profile.html')

@app.route("/login")
def login():
    return render_template('login.html')

@login_is_required
@app.route("/auth_home")

def auth_home():
    return render_template('auth_home.html')


##################################################################### RenderTemplate #############################################################







##################################################################### RunApp #####################################################################

if __name__ == "__main__":
    app.run(debug=True)

##################################################################### RunApp #####################################################################   