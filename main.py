from flask import Flask, render_template, redirect, request

# Import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import DB Modules
import requests
import re


from db_setup import Base,Admin

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

@app.route('/')
def HelloWorld():
    return render_template('dashboard.html')

#function to validate url
URL_RE = re.compile(r"^[a-zA-Z0-9_-]{1,10}$")
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
USER_RE = re.compile(r"^[a-zA-Z]{1,20}$")
def validateName(name):
    return USER_RE.match(name)

# regex expressions to check for email validation
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def validateEmail(email):
    if EMAIL_RE.match(email):
        return True
    return False

# regex expressions to checl for mobile validation
MOB_RE = re.compile(r'^[0-9]{7,13}$')
def validateMob(mob):
    if MOB_RE.match(mob):
        return True
    return False

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
            return render_template('signup.html',error = "NullValues")
        if not validateName(name):
            return render_template('signup.html',error = "nameError")
        if not validateEmail(email):
            return render_template('signup.html',error = "emailError")
        if not validateUrl(url):
            return render_template('signup.html',error = "urlError")
        if not validateMob(mob):
            return render_template('signup.html',error = "mobError")
        else:
            user = Admin()
            user.name = name
            user.url = url
            user.mobile = mob
            user.password = password
            user.email = email

            conn.add(user)
            conn.commit()
            return "Sucess"

    else:
        return render_template('signup.html',error = "")

@app.route('/login')
def Login():
    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = 'itstimetomoveon'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
