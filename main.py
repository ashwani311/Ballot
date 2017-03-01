from flask import Flask, render_template
app = Flask(__name__)
#--- App configration

@app.route('/signup')
def SignUp():
    print "Hello World"
    return render_template('signup.html')
    

if __name__ == '__main__':
    app.secret_key = 'itstimetomoveon'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)