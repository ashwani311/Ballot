from flask import Flask, render_template, redirect, request, url_for, session

# Import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import DB Modules
import requests
import re


from db_setup import Base, Admin, Ballot, Voter, Option

# ---------------------------------------------------------------------
#                         App configration
# ---------------------------------------------------------------------
app = Flask(__name__)

# create engine connection with sql library

engine = create_engine('sqlite:///OBallot.db')

# bind the engine with base class

Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

conn = DBSession()
app = Flask(__name__)
#--- App configration

#--- Validation Functions --------#


#function to validate url
URL_RE = re.compile(r"^[a-zA-Z0-9_-]{1,30}$")
def validateUrl(url):
    if URL_RE.match(url):
        urlQuery = conn.query(Admin).filter_by(url=url).one_or_none()
        if not urlQuery:
            return True
    return False

#function to validate for null values
def validateNull(data):
    for key in data:
        if data[key] == "":
            return True
    return False

# regex expressions to check for  username validation
USER_RE = re.compile(r"^[a-zA-Z ]{1,20}$")
def validateName(name):
    if USER_RE.match(name):
        return True
    return False

USERNAME_RE = re.compile(r"^[a-zA-Z]{1,20}$")
def validateUname(name):
    if USERNAME_RE.match(name):
        return True
    return False

# regex expressions to check for email validation
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def validateEmail(email):
    if EMAIL_RE.match(email):
        emailQuery = conn.query(Admin).filter_by(email=email).one_or_none()
        if not emailQuery:
            return True
    return False

# regex expressions to checl for mobile validation
MOB_RE = re.compile(r'^[0-9]{7,13}$')
def validateMob(mob):
    if MOB_RE.match(mob):
        return True
    return False

# --------- Validation Ends ----------------#

# --------- Help Functions -----------------#

def isLogged():
    if 'logged' in session and session['logged']:
        email = session['email'];
        admin = conn.query(Admin).filter_by(email=email).one_or_none()
        return admin
    return False

def log_user(email):
    session['logged'] = True
    session['email'] = email


def isAdmin(email,password):
    if EMAIL_RE.match(email):
        admin = conn.query(Admin).filter_by(email=email).one_or_none()
        if admin:
            if admin.password == password:
                return True

    return False


@app.route('/')
def Root():
    admin = isLogged()
    if admin:
        return redirect(url_for('Dashboard',url = admin.url))
    else:
        return redirect(url_for('Login'))



@app.route('/signup',methods=['GET', 'POST'])
def Signup(error = ""):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mob = request.form['mob']
        password = request.form['pass']
        url = request.form['url']
        confirmPassword = request.form['cpass']
        params = dict()
        params['name'] = name
        params['email'] = email
        params['mob'] = mob
        params['password'] = password
        params['url'] = url
        if validateNull(params):
            return render_template('signup.html',error = "nullValues")
        del params
        if not validateName(name):
            return render_template('signup.html',error = "nameError")
        if not validateEmail(email):
            return render_template('signup.html',error = "emailError")
        if not validateUrl(url):
            return render_template('signup.html',error = "urlError")
        if not validateMob(mob):
            return render_template('signup.html',error = "mobError")
        if confirmPassword == password:
            user = Admin()
            user.name = name
            user.url = url
            user.mobile = mob
            user.password = password
            user.email = email
            conn.add(user)
            conn.commit()
            return redirect(url_for('Login'))
        else:
            return render_template('signup.html',error = "matchError")

    else:
        return render_template('signup.html',error = "")

@app.route('/login',methods=['GET', 'POST'])
def Login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']

        params = dict()
        params['email'] = email
        params['password'] = password

        if validateNull(params):
            return render_template('login.html',error = "nullValues")
        del params

        if isAdmin(email,password):
            log_user(email)
            admin = conn.query(Admin).filter_by(email=email).one_or_none()
            return redirect(url_for('Dashboard',url = admin.url))

        else:
            return render_template('login.html',error = "wrongLogin")

    else:
        return render_template('login.html')

@app.route('/dashboard/<string:url>')
def Dashboard(url):
    admin = isLogged()
    if admin:
        if admin.url == url:
            ballot = conn.query(Ballot).filter_by(url = url).one_or_none()
            return render_template('dashboard.html',ballot = ballot,admin = admin,error = "")
        else:
            return redirect(url_for('Dashboard',url = admin.url))
    else:
        return redirect(url_for('Login'))

#-----  Dashboard Post Handlers -------#
@app.route('/dashboard/<string:url>/<string:error>')
def DashErrorHandler(url,error):
    admin = isLogged()
    if admin:
        if admin.url == url:
            ballot = conn.query(Ballot).filter_by(url = url).one_or_none()
            return render_template('dashboard.html',ballot = ballot,admin = admin, error = error)
        else:
            return redirect(url_for('Dashboard',url = admin.url))
    else:
        return redirect(url_for('Login'))


@app.route('/dashboard/<string:url>/new',methods = ['POST'])
def NewBallot(url):
    admin = isLogged()
    if admin:
        if admin.url == url:
            name = request.form['name']
            date = request.form['date']
            param = dict()
            param['name'] = name
            param['date'] = date
            if validateNull(param):
                error = "nullValues"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            if validateUname(name):
                error = "nameError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            if validateDate(date):
                error = "dateError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
        else:
            return redirect(url_for('DashErrorHandler',url = admin.url, error = "InvalidUrl"))
    else:
        return redirect(url_for('Login'))

if __name__ == '__main__':
    app.secret_key = 'itstimetomoveon'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
