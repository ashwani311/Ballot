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
def validateUrl(url):
    urlQuery = session.query(Admin).filter_by(url=url).one_or_none()

#function to validate for null values
def validateNull(**data):
    if (data['name']=="" or data['password']=="" or data['email']=="" or data['mob']=="" or data['url']==""):
        return False

    return True

# regex expressions to check for  username validation
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{1,10}$")
def validateName(name):
    return name and USER_RE.match(name)

# regex expressions to check for email validation
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def validateEmail(email):
    if(not email or EMAIL_RE.match(email)):
        error = "email Id not valid"
        return error
    return ""

@app.route('/signup',methods=['GET', 'POST'])
def Signup():
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

        if (not validateNull(**params)):
            params['error'] = "Required Field's can't be empty"
            return render_template('signup.html', **params)

        params['error'] = validateEmail(email)
        if(params['error']!= ""):
            return render_template('signup.html', **params)
        else:
            user = Admin()
            user.name = name
            user.url = url
            user.mobile = mob
            user.password = password
            user.email = email

            conn.add(user)
            conn.commit()
            return redirect('/sucess')

    else:
        return render_template('signup.html')

@app.route('/login')
def Login():
    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = 'itstimetomoveon'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
