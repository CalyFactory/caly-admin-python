from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import make_response
from flask import session
import os
import uuid
import db_manager
import datetime

app = Flask(__name__)
def fetch_all_json(result):
    lis = []
    
    for row in result.fetchall():
        i = 0
        dic = {}
        
        for data in row:
            if type(data) == datetime:
                dic[result.keys()[i]]= str(data)
            else:
                dic[result.keys()[i]]= str(data)
            if i == len(row)-1:
                lis.append(dic)
            
            i=i+1
    return lis

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

    return response

@app.route("/admin", methods= ["GET"])
def page_admin_get():
    if 'caly_admin_name' not in session:
        return redirect("/login")
    result = fetch_all_json(
        db_manager.query(
            """
            SELECT register, count(register)
            FROM calydb.RECOMMENDATION 
            GROUP BY register
            """
        )
    )
    write_result = {}
    for row in result:
        if row['register'] != 'None':
            write_result[row['register']] = row['count(register)']
    
    result = fetch_all_json(
        db_manager.query(
            """
            SELECT * FROM RECOMMENDATION
            ORDER BY 
            created DESC
            limit 30;
            """
        )
    )
    reco_result = []
    for row in result:
        print(row['reco_hashkey'])
        if row['register'] != 'None':
            reco_result.append(row)

    return render_template('admin.html', write_result = write_result, reco_result = reco_result)

@app.route("/admin", methods=["POST"])
def page_admin_post():
    reco_register = session['caly_admin_name']
    reco_region = request.form['region']
    reco_category = request.form['category']
    reco_age = request.form['age']
    reco_gender = request.form['gender']
    reco_title = request.form['title']
    reco_img = request.files['img']
    reco_imgfile = randomfilename(reco_img.filename)
    reco_img.save(os.path.join('./img/', reco_imgfile))

    reco_address = request.form['address']
    reco_distance = request.form['distance']
    reco_price = request.form['price']
    reco_map = request.form['map_url']
    reco_deep = request.form['deep_url']

    reco_hashkey = str(uuid.uuid4())
    db_manager.query(
        """
        INSERT INTO RECOMMENDATION
        (
            reco_hashkey,
            region,
            category,
            age,
            gender,
            title,
            img_url,
            address,
            price,
            map_url,
            register,
            deep_url,
            distance
        )
        VALUES
        (
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s,
            %s
        );
        """
        ,
        (
            reco_hashkey,
            reco_region,
            reco_category,
            reco_age,
            reco_gender,
            reco_title,
            reco_imgfile,
            reco_address,
            reco_price,
            reco_map,
            reco_register,
            reco_deep,
            reco_distance
        )
    )

    
    return redirect('/admin')

@app.route("/admin", methods=["DEL"])
def page_admin_del():
    session.pop['caly_admin_name']
    return redirect('/login')

def randomfilename(filename):
    filetype = ''.join(filename.split('.')[-1])
    return str(uuid.uuid4())+"."+str(filetype)

app.secret_key = "aaaaa"
app.run(host='0.0.0.0', port = 5000)

print("hi")