from flask import Flask, render_template, redirect, request, url_for, session
import datetime as dt
# Import SQLAlchemy

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import DB Modules
import requests
import re
import random
import string


from db_setup import Base, Admin, Ballot, Voter, Option, Vote, Log

# Authy Modules
from authy.api import AuthyApiClient
authy_api = AuthyApiClient('UQz047MGN2RBNZM0k08xllWsKE0x0KdE')

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
        if len(str(mob)) == 10:
            return True
    return False


def validateDate(date):
    format = "%Y/%m/%d"
    date = dt.datetime.strptime(date, format).date()
    now = dt.datetime.now().date()
    if(date < now):
        return False
    return date

def isPalindrome(s):
    return s == s[::-1]


def has_previous(name,url,date):
    ballot = conn.query(Ballot).filter_by(name=name,url=url,date=date).one_or_none()
    if ballot:
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

def allow_vote(id,bid):
    session['vote'] = True
    session['id'] = id
    session['bid'] = bid

def isVoteAllowed():
    if 'vote' in session and session['vote']:
        bid = session['bid']
        ballot = conn.query(Ballot).filter_by(id = bid).one_or_none()
        return ballot
    return None

def endVoteAccess():
    del session['vote']
    del session['id']
    del session['bid']

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
            count = dict()
            if ballot:
                candidates = conn.query(Option).filter_by(bid = ballot.id)
                voters = conn.query(Voter).filter_by(bid = ballot.id)
                count['candidates'] = candidates.count()
                count['voters'] = voters.count()
                candidates = candidates.all()
                voters = voters.all()
            else:
                candidates = None
                voters = None
                count['candidates'] = 0
                count['voters'] = 0
            return render_template('dashboard.html',ballot = ballot,admin = admin,error = "",candidates = candidates,voters = voters,count = count)
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
            count = dict()
            if ballot:
                candidates = conn.query(Option).filter_by(bid = ballot.id)
                voters = conn.query(Voter).filter_by(bid = ballot.id)
                count['candidates'] = candidates.count()
                count['voters'] = voters.count()
                candidates = candidates.all()
                voters = voters.all()
            else:
                candidates = None
                voters = None
                count['candidates'] = 0
                count['voters'] = 0
            return render_template('dashboard.html',ballot = ballot,admin = admin,error = "",candidates = candidates,voters = voters,count = count)
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
            if not validateUname(name):
                error = "nameError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            date = validateDate(date)
            print date
            if not date:
                error = "dateError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            if has_previous(name,url,date):
                error = "hasPrevious"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            ballot = Ballot()
            ballot.name = name
            ballot.date = date
            ballot.url = url
            conn.add(ballot)
            conn.commit()
            return redirect(url_for('Dashboard',url = admin.url))

        else:
            return redirect(url_for('DashErrorHandler',url = admin.url, error = "InvalidUrl"))
    else:
        return redirect(url_for('Login'))


@app.route('/dashboard/<string:url>/<int:bid>/candidate',methods = ['POST'])
def NewCandidate(url,bid):
    admin = isLogged()
    if admin:
        if admin.url == url:
            name = request.form['cname']
            desc = request.form['description']
            param = dict()
            param['name'] = name
            if validateNull(param):
                error = "nullValues"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            if not validateUname(name):
                error = "nameError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            name = name.lower()
            b = conn.query(Ballot).filter_by(id = bid).one_or_none()
            if url != b.url:
                error = "urlError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            allcandidates = conn.query(Option).filter_by(bid = b.id).count()
            if allcandidates >= 4:
                error = "maxCandidates"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            previous = conn.query(Option).filter_by(name = name).one_or_none()
            if previous:
                error = "candidateExist"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            candidate = Option()
            candidate.name = name
            candidate.discription = desc
            candidate.bid = b.id
            conn.add(candidate)
            conn.commit()
            return redirect(url_for('Dashboard',url = admin.url))

        else:
            return redirect(url_for('DashErrorHandler',url = admin.url, error = "InvalidUrl"))
    else:
        return redirect(url_for('Login'))

@app.route('/dashboard/<string:url>/<int:bid>/voter',methods = ['POST'])
def NewVoter(url,bid):
    admin = isLogged()
    if admin:
        if admin.url == url:
            name = request.form['username']
            mob = request.form['mobile']
            param = dict()
            param['name'] = name
            param['mob'] = mob
            if validateNull(param):
                error = "nullValues"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            if not validateUname(name):
                error = "nameError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            name = name.lower()
            if not validateMob(mob):
                error = "mobError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            b = conn.query(Ballot).filter_by(id = bid).one_or_none()
            if url != b.url:
                error = "urlError"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            previous = conn.query(Voter).filter_by(uname = name,bid = bid).one_or_none()
            if previous:
                error = "voterExist"
                return redirect(url_for('DashErrorHandler',url = admin.url, error = error))
            password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            while isPalindrome(password):
                password = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
            voter = Voter()
            voter.uname = name
            voter.password = password
            voter.mobile = mob
            voter.bid = b.id
            conn.add(voter)
            conn.commit()
            user = authy_api.users.create('new_user@email.com', mob, 91)
            if user.ok():
                print "user added"
            return redirect(url_for('Dashboard',url = admin.url))

        else:
            return redirect(url_for('DashErrorHandler',url = admin.url, error = "InvalidUrl"))
    else:
        return redirect(url_for('Login'))


@app.route('/vote/<string:url>',methods = ['GET','POST'])
def VoteLogin(url):
    if request.method == 'POST':
        name = request.form['name']
        mob = request.form['mob']
        param = dict()
        param['name'] = name
        param['mob'] = mob
        now = dt.datetime.now().date()
        ballot = conn.query(Ballot).filter_by(url = url,date = now).one_or_none()
        if validateNull(param):
            error = "nullValues"
            return render_template('vote_login.html',error = error ,ballot = ballot)
        if not validateUname(name):
            error = "nameError"
            return render_template('vote_login.html',error = error ,ballot = ballot)
        name = name.lower()
        if not validateMob(mob):
            error = "mobError"
            return render_template('vote_login.html',error = error ,ballot = ballot)
        if url != ballot.url:
            error = "urlError"
            return render_template('vote_login.html',error = error ,ballot = ballot)
        voter = conn.query(Voter).filter_by(uname = name,bid = ballot.id).one_or_none()
        authy_api.phones.verification_start(mob, 91, via='sms', locale='en')
        allow_vote(voter.id,ballot.id)
        return redirect(url_for('Vote'))

    else:
        now = dt.datetime.now().date()
        ballot = conn.query(Ballot).filter_by(url = url,date = now).one_or_none()
        return render_template('vote_login.html',error = "No Ballot Found" ,ballot = ballot)

@app.route('/vote')
def Vote():
    ballot = isVoteAllowed()
    if ballot:
        return render_template('vote.html',ballot = ballot)


@app.route('/admins')
def Admins():
    admins = conn.query(Admin).all()
    return render_template('admins.html',admins = admins)


@app.route('/logout')
def logOut():
    session['logged'] = False
    del session['email']
    return redirect(url_for('Login'))

if __name__ == '__main__':
    app.secret_key = 'itstimetomoveon'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
