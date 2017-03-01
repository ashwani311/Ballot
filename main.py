from flask import Flask, render_template
app = Flask(__name__)
#--- App configration

@app.route('/signup')
def Signup():
    return render_template('signup.html')

@app.route('/login')
def Login():
    return render_template('login.html')

if __name__ == '__main__':
    app.secret_key = 'itstimetomoveon'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)