from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import make_response
from flask import session
from flask import send_from_directory
import requests
import os
import uuid
import db_manager
import datetime
import crawl
import json


app = Flask(__name__, static_url_path='/img', static_folder='img')
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



##api
@app.route("/getMangoInfo",methods = ["GET"])
def getMangoInfo():
    region = request.args['region']
    result = crawl.getBestPointList(region)
    # print (str(result))
    return json.dumps(result)

@app.route("/getDetailInfo",methods = ["GET"])
def getDetailInfo():
    url = request.args['url']
    result = crawl.getDetailInfo(url)
    # print (str(result))
    return json.dumps(result)    

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
        if row['register'] != 'None':
            reco_result.append(row)

    result = fetch_all_json(
        db_manager.query(
            """
            SELECT tag_name 
            FROM HASHTAG 
            order by tag_name ASC
            LIMIT 10000;
            """
        )
    )

    hashtags=""
    for row in result:
        hashtags+="#"+row['tag_name']+" "

    search_result = []
    if 'search' in request.args:
        print("search")
        
        if 'onlymy' in request.args:
            search_result = fetch_all_json(
                db_manager.query(
                    """
                    SELECT *
                    FROM RECOMMENDATION
                    WHERE
                    title like %s   AND 
                    register = %s
                    ORDER BY 
                    created DESC
                    """
                    ,
                    (
                        "%"+request.args.get('searchtext')+"%",
                        session['caly_admin_name']
                    )
                )
            )
        else:
            search_result = fetch_all_json(
                db_manager.query(
                    """
                    SELECT *
                    FROM RECOMMENDATION
                    WHERE
                    title like %s  
                    ORDER BY 
                    created DESC
                    """
                    ,
                    (
                        "%"+request.args.get('searchtext')+"%",
                    )
                )
            )
        
        print(result)


    return render_template(
        'admin.html', 
        write_result = write_result, 
        reco_result = reco_result, 
        hashtags = hashtags, 
        search_result = search_result
    )

@app.route("/admin", methods=["POST"])
def page_admin_post():

    if 'caly_admin_name' not in session:
        return redirect("/login")
    if 'logout' in request.form:
        session.pop('caly_admin_name')
        return redirect('/login')
    if 'delete' in request.form:
        hashkey = request.form['delete']
        db_manager.query(
            """
            DELETE FROM RECOMMENDATION
            WHERE 
            `reco_hashkey` = %s
            """
            ,
            (
                hashkey,
            )
        )
        return redirect("/admin")
    

    reco_register = session['caly_admin_name']
    reco_region1 = request.form['region1']
    reco_category = request.form['category']
    reco_region2 = request.form['region2']
    reco_gender = request.form['gender']
    reco_title = request.form['title']
    reco_source = request.form['source_url']
    


    if 'instagram' in reco_source:
        source_user_id  = crawl.getInstaId(reco_source)
        print(source_user_id);
        print("instagram")
        result = requests.post(
            'http://www.dinsta.com/photos/',
            data = {
                'url': reco_source
            }
        ).text

        tag_start = result.find("<img src=") + 10
        tag_end = result.find("\"", tag_start)

        img_url = result[tag_start:tag_end]
        reco_imgfile = randomFileName(img_url)

        with open("img/"+reco_imgfile, 'wb') as f:
            f.write(requests.get(img_url).content)
    else:
        if request.files['img'].filename == '':
            reco_imgfile = ""
        else:
            reco_img = request.files['img']
            reco_imgfile = randomFileName(reco_img.filename)
            reco_img.save(os.path.join('./img/', reco_imgfile))

    reco_address = request.form['address']
    reco_distance = request.form['distance']
    reco_price = request.form['price']
    reco_map = request.form['map_url']

    location_info  = crawl.getLatLanFromMapUrl(reco_map)

    lat = '0';
    lng = '0';

    if 'lat' in location_info:
        lat = location_info['lat']
        lng = location_info['lng']

    reco_deep = request.form['deep_url']
    reco_hashtags = request.form['hashtags']
    reco_memo = request.form['memo']
    reco_hashkey = str(uuid.uuid4())
    hashtaglist = reco_hashtags.split('/')


    for hashtag in hashtaglist:
        print(hashtag)
        result = fetch_all_json(
            db_manager.query(
                """
                SELECT * 
                FROM HASHTAG 
                WHERE 
                tag_name = %s
                """
                ,
                (
                    str(hashtag),
                )
            )
        )
        if len(result)==0:
            db_manager.query(
                """
                INSERT INTO HASHTAG 
                (`tag_name`)
                VALUES 
                ( %s )
                """
                ,
                (
                    str(hashtag),
                )
            )
        tagId = fetch_all_json(
            db_manager.query(
                """
                SELECT * 
                FROM HASHTAG 
                WHERE 
                tag_name = %s
                """
                ,
                (
                    str(hashtag),
                )
            )
        )[0]['code']

        db_manager.query(
            """
            INSERT INTO RECO_HASHTAG 
            (`reco_hashkey`, `hash_code`)
            VALUES
            ( %s, %s )
            """
            ,
            (
                reco_hashkey,
                tagId
            )
        )

    db_manager.query(
        """
        INSERT INTO RECOMMENDATION
        (
            reco_hashkey,
            region,
            category,
            main_region,
            gender,
            title,
            img_url,
            address,
            price,
            map_url,
            register,
            deep_url,
            distance,
            memo,
            source_url,
            lat,
            lng,
            source_user_id
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
            reco_region2,
            reco_category,
            reco_region1,
            reco_gender,
            reco_title,
            reco_imgfile,
            reco_address,
            reco_price,
            reco_map,
            reco_register,
            reco_deep,
            reco_distance,
            reco_memo,
            reco_source,
            lat,
            lng,
            source_user_id
        )
    )

    
    return redirect('/admin')

@app.route("/admin/edit", methods=["GET"])
def page_edit_get():

    print(request.args['hashkey'])
    result = fetch_all_json(
        db_manager.query(
            """
            SELECT * 
            FROM RECOMMENDATION
            WHERE 
            reco_hashkey = %s
            """
            ,
            (
                request.args['hashkey'],
            )
        )
    )
    data = result[0]

    result = fetch_all_json(
        db_manager.query(
            """
            SELECT *
            FROM RECO_HASHTAG
            RIGHT JOIN HASHTAG
            ON RECO_HASHTAG.hash_code = HASHTAG.code
            WHERE 
            reco_hashkey = %s
            """
            ,
            (
                request.args['hashkey'],
            )
        )
    )

    c = 0
    for row in result:
        if c==0:
            data['hashtags'] = row['tag_name']
        else:
            data['hashtags']+= "/" + row['tag_name']
        c+=1

    print(data)

    return render_template(
        'edit.html',
        data = data
    )

@app.route("/admin/edit", methods = ["POST"])
def page_edit_post():

    reco_hashkey = request.form['reco_hashkey']
    reco_register = session['caly_admin_name']
    reco_region1 = request.form['region1']
    reco_category = request.form['category']
    reco_region2 = request.form['region2']
    reco_gender = request.form['gender']
    reco_title = request.form['title']
    reco_memo = request.form['memo']
    reco_source = request.form['source_url']


    if 'instagram' in reco_source:
        source_user_id  = crawl.getInstaId(reco_source)
        print("instagram")
        result = requests.post(
            'http://www.dinsta.com/photos/',
            data = {
                'url': reco_source
            }
        ).text

        tag_start = result.find("<img src=") + 10
        tag_end = result.find("\"", tag_start)

        img_url = result[tag_start:tag_end]
        reco_imgfile = randomFileName(img_url)

        with open("img/"+reco_imgfile, 'wb') as f:
            f.write(requests.get(img_url).content)
    else:
        if request.files['img'].filename == '':
            reco_imgfile = request.form['img_before']
        else:
            reco_img = request.files['img']
            reco_imgfile = randomFileName(reco_img.filename)
            reco_img.save(os.path.join('./img/', reco_imgfile))

    reco_address = request.form['address']
    reco_distance = request.form['distance']
    reco_price = request.form['price']
    reco_map = request.form['map_url']
    location_info  = crawl.getLatLanFromMapUrl(reco_map)

    lat = '0';
    lng = '0';

    if 'lat' in location_info:
        lat = location_info['lat']
        lng = location_info['lng']

    reco_deep = request.form['deep_url']
    reco_hashtags = request.form['hashtags']

    db_manager.query(
        """
        UPDATE RECOMMENDATION
        SET  
        main_region = %s,
        region = %s, 
        category = %s,
        gender = %s,
        title = %s,
        img_url = %s,
        address = %s,
        price = %s,
        map_url = %s,
        deep_url = %s,
        distance = %s,
        memo = %s,
        source_url = %s,
        lat = %s,
        lng = %s,
        source_user_id = %s
        WHERE 
        reco_hashkey = %s
        """
        ,
        (
            reco_region1,
            reco_region2,
            reco_category,
            reco_gender,
            reco_title,
            reco_imgfile,
            reco_address,
            reco_price,
            reco_map,
            reco_deep,
            reco_distance,
            reco_memo,
            reco_source,            
            lat,
            lng,
            source_user_id,
            reco_hashkey
        )
    )
    

    return redirect("admin")

def randomFileName(filename):
    filetype = ''.join(filename.split('.')[-1])
    return str(uuid.uuid4())+"."+str(filetype)

app.secret_key = "aaaaa"
app.run(host='0.0.0.0', port = 7070, debug=True)

print("hi")
