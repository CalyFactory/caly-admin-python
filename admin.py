from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import make_response
from flask import session

app = Flask(__name__)

@app.route("/")
def hello():
    return redirect("/login", code=302)

@app.route("/login", methods = ["GET"])
def page_login_get():
    if 'caly_admin_name' in session:
        return redirect("/admin")
    return render_template('login.html')

@app.route("/login", methods = ["POST"])
def page_login_post():
    response = make_response(redirect("/admin"))

    session['caly_admin_name'] = request.form['name']
    #response.set_cookie("caly_admin_name", request.form['name'])

    return response

@app.route("/admin")
def admin():
    return session['caly_admin_name']
#    return request.cookies.get('caly_admin_name')

app.secret_key = "aaaaa"
app.run(host='0.0.0.0', port = 5000)

print("hi")