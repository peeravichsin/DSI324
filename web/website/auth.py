from flask import Blueprint, session, abort, redirect, request,render_template,flash,url_for
import flask
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
import google.auth.transport.requests
from pip._vendor import cachecontrol
import os
import pathlib
from os import path
import requests
from datetime import datetime
from flask_mysqldb import MySQLdb
from . import mysql

auth = Blueprint('auth', __name__)



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


@auth.route("/Glogin")
def Glogin():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@auth.route("/callback")
def callback():
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
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
    session["picture"] = id_info.get("picture")
    if '@dome.tu.ac.th' in session["email"] :
        cur.execute('select * from login where user_id = %s',(session["google_id"],))
        user = cur.fetchone()
        if user:
            flash(f'Welcome { session["name"] }', category='success')
            return redirect("/auth_home")
        else:
            return redirect("/sign_up")
    elif '@dome.tu.ac.th' not in session['email']:
        flash('You are not allow to login', category='error')
        return redirect("/login")



@auth.route("/sign_up",methods =['GET','POST'])
def signup():
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        user_id = session["google_id"]
        user_email = session["email"]
        student_email = session["email"]
        name = session["name"].split(' ')
        student_fname_en = name[0]
        student_lname_en = name[1]
        student_fname_th = request.form.get('student_fname_th')
        student_lname_th = request.form.get('student_lname_th')
        student_id = request.form.get('student_id')
        faculty_id = 24
        major_id = request.form.get('major_name')
        year = student_id[:2]
        current_time = datetime.now()
        study_year = str(int(str(int(current_time.year)+543)[2:4])-int(year))
    
       
        cur.execute("insert into login(user_id,user_email) values(%s,%s)",(user_id,user_email))
        mysql.connection.commit()

        cur.execute("insert into student(student_id,student_fname_th,student_lname_th,student_fname_en,student_lname_en,student_email,user_id,major_id,faculty_id,study_year) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                            (student_id,student_fname_th,student_lname_th,student_fname_en,student_lname_en,student_email,user_id,major_id,faculty_id,study_year)
                                            )
        mysql.connection.commit()

        flash('Profile created!', category='success')
        return redirect('/auth_home')
        
    return render_template('sign_up.html')
   


@auth.route("/logout")
@login_is_required
def logout():
    session.clear()
    return redirect("/")

