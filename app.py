import json
import pyrebase
import psycopg2
import base64
from flask import Flask, request, jsonify, render_template,redirect
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import time
import datetime
from datetime import timedelta
import requests
from flask_jwt_extended import JWTManager,create_access_token,create_refresh_token,set_access_cookies,jwt_required,set_refresh_cookies,get_jwt_identity,unset_jwt_cookies,get_jwt,get_jwt,verify_jwt_in_request

# Các mã lỗi
# 200: Success OK
# 400: Bad Request
# 401: Unauthorized
# 404: Not found
# 405: Method not allowed
# 422: Unprocessable Entity
# ===============================
# ===============================
# ===============================

#===== Connect to PostgreSQL in Heroku add on===========
con = psycopg2.connect(database="d3pbrmjh5hgsb9", user="cuefzkwkvdoncc", password="3b5a03ed19cb22bbb695c2b1763d6a7035e2beb9e97221330a9e209500e1c3b8", host="ec2-52-71-231-37.compute-1.amazonaws.com", port="5432")
app = Flask(__name__)

#==== config for cookie========
app.config['JWT_SECRET_KEY']='APISIMPLEAPP'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=1)
jwt= JWTManager(app)

# =========Fire base config=================
config = {
    "apiKey": "AIzaSyBYF170a8oXKkqgQrrfoPnZpa45a5AlGTI",
    "authDomain": "imgapi-144fe.firebaseapp.com",
    "databaseURL": "https://imgapi-144fe.firebaseio.com",
    "projectId": "imgapi-144fe",
    "storageBucket": "imgapi-144fe.appspot.com",
    "messagingSenderId": "888978133916",
    "appId": "1:888978133916:web:89c5a046ba04f30ad76e59",
    "measurementId": "G-6KX9HTXCGK"
}
firebase= pyrebase.initialize_app(config)
storage= firebase.storage()

# storage.child("/img").delete('Screenshot (7).png')
# storage.path('/img/Screenshot (7).png').delete()

# ============ Another function==============
# ===============================
# ===============================
# ===============================
def myconverter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

def checkuser(email):
    cur = con.cursor()
    cur.execute("SELECT id_account from account where email='"+str(email)+"'")
    rows = cur.fetchall()
    if len(rows) !=0:
        return True
    else:
        return False

def checkpass(email,password):
    cur = con.cursor()
    cur.execute("SELECT id_account from account where password='"+str(password)+"' and email='"+str(email)+"'")
    rows = cur.fetchall()
    if len(rows) !=0:
        return True
    else:
        return False

def getuserid(email):
    cur = con.cursor()
    cur.execute("SELECT id_account from account where email='"+str(email)+"'")
    rows = cur.fetchall()
    if len(rows) !=0:
        return rows[0][0]
    else:
        return ""

def getusername(email):
    cur = con.cursor()
    cur.execute("SELECT username from account where email='"+str(email)+"'")
    rows = cur.fetchall()
    if len(rows) !=0:
        return rows[0][0]
    else:
        return ""

def getuserrole(email):
    cur = con.cursor()
    cur.execute("SELECT role from account where email='"+str(email)+"'")
    rows = cur.fetchall()
    return rows[0][0]

def get_identity_if_logedin():
    verify_jwt_in_request(optional=True)
    return get_jwt_identity()

def check_post_exist(id_post):
    cur = con.cursor()
    cur.execute("SELECT rating from post where id_post='"+str(id_post)+"'")
    rows = cur.fetchall()
    if len(rows) != 0:
        return True
    else:
        return False

def check_category_exist(id_category):
    cur = con.cursor()
    cur.execute("SELECT id_category from category where id_category='"+str(id_category)+"'")
    rows = cur.fetchall()
    if len(rows) != 0:
        return True
    else:
        return False

def check_account_exist(id_account):
    cur = con.cursor()
    cur.execute("SELECT id_account from account where id_account="+str(id_account))
    rows = cur.fetchall()
    if len(rows) != 0:
        return True
    else:
        return False

def check_category_exist(id_category):
    cur = con.cursor()
    cur.execute("SELECT id_category from category where id_category="+str(id_category))
    rows = cur.fetchall()
    if len(rows) != 0:
        return True
    else:
        return False

# ========== Main function ============
# ===============================
# ===============================
# ===============================

#======= LOGIN +GET + HEADER(email,password)
#======= return status
#======= 1: unvalid- username + 401
#======= 2: unvalid- password + 401
#======= 0: success- + 200 + access_token + refresh_token + user + role
#======= 3: logedin
@app.route('/login', methods=['GET'])
def login():
    user_indentify = get_identity_if_logedin()
    if user_indentify == None:
         # Get email & password from header + get request for mobile and web
        email= request.headers.get('email')
        password= request.headers.get('password')
        if checkuser(email)== False:
            return jsonify({'status':1}),401
        else:
            if checkpass(email,password)== False:
                return jsonify({'status':2}),401
            else:
                username= getusername(email)
                idaccount= getuserid(email)
                role= getuserrole(email)
                # add role vào jwt để giữ luôn cả role trong access cookie
                additional_claims = {"role":role}
                access_token = create_access_token(email, additional_claims=additional_claims)
                refresh_token = create_refresh_token(identity=email)
                resp=jsonify(idaccount=idaccount,status=0,access_token=access_token,refresh_token=refresh_token,email=email,role=role,username=username)
                set_access_cookies(resp,access_token)
                return resp,200
    else:
        claims = get_jwt()
        username= getusername(claims['sub'])
        idaccount= getuserid(claims['sub'])
        return jsonify({'status':3,'role':claims['role'],'email':claims['sub'],'username':username,'idaccount':idaccount}),200


#======= LOGOUT + GET
#======= return status
#======= 1: success + 200
#======= ở đây chỉ xóa cookie chứ chưa vô hiệu hóa cookie (xử lí bằng cách đưa cookie vào blacklist và check nó)
@app.route("/logout", methods=["GET"])
@jwt_required(refresh=True)
def logout():
    response = jsonify({"status":1})
    unset_jwt_cookies(response)
    return response,200

#===== access_token Expired --> Use RefreshToken to post --> receive new accesstoken
#======= refresh + GET
#======= return status
#======= 1: success + 200
@app.route("/refresh", methods=["GET"])
@jwt_required(refresh=True)
def refresh():
    email = get_jwt_identity()
    role=getuserrole(email)
    additional_claims = {"role":role}
    access_token = create_access_token(email, additional_claims=additional_claims)
    return jsonify(access_token=access_token,status=1),200

# ========= View =====
# ========= Add view when user read post
# ========= return status 
@app.route('/post/view/<int:id_post>',methods=['POST'])
def add_view_to_post(id_post):
    if not check_post_exist:
        return jsonify({"status":0}),200
    cur = con.cursor()
    cur.execute("update post set rating= rating + "+str(1)+" where id_post='"+str(id_post)+"'")
    con.commit()
    return jsonify({"status":1}),200

# ========== Duyệt bài======
# ========== Return status
# 0- Not Allow
# 1- Allow
# 2- Not Exist Post
@app.route('/post/approve/<int:id_post>',methods=['POST'])
@jwt_required()
def post_approve(id_post):
    if not check_post_exist(id_post):
        return jsonify({"status":2}),200
    myjwt=get_jwt()
    role=myjwt['role']
    # Có quyền chỉnh sửa
    if role == 1:
        cur = con.cursor()
        cur.execute("update post set status=1 where id_post='"+str(id_post)+"'")
        con.commit()
        return jsonify({"status":1}),200
    # Không có quyền chỉnh sửa
    elif role == 0:
        return jsonify({"status":0}),200

# ========== Xóa bài viết =======
# ========== Return status
# 0: not allow
# 1: allow --> success
@app.route('/post/del/<int:id_post>',methods=['POST'])
@jwt_required()
def post_del(id_post):
    if not check_post_exist(id_post):
        return jsonify({"status":2}),200
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({"status":0}),200
    elif role == 1:
        cur = con.cursor()
        cur.execute("DELETE FROM post WHERE id_post=%s;",(id_post,))
        con.commit()
        return jsonify({"status":1}),200

# ========== Thêm bài viết=======
# ========== Return status
# 0: not allow
# 1: allow - not contains title
# 2: allow - not contains content
# 3: allow - not contains category
# 4: allow - not exists categroy
# 5: allow - not contains img
# 6: success
@app.route('/post/add',methods=['POST'])
@jwt_required()
def post_add():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({"status":0}),200

    # {"title":"abc","content":"content","category":1,"img":"imgstr"}
    myjson = request.get_json()
    myjson = json.loads(myjson) 

    title= myjson['title']
    title=title.strip()
    if not title:
        return jsonify({"status":1}),200

    content= myjson['content']
    content= content.strip()
    if not content:
        return jsonify({"status":2}),200

    if not myjson['category']:
        return jsonify({"status":3}),200
    if not check_category_exist(int(myjson['category'])):
        return jsonify({"status":4}),200
        
    id_category= int(myjson['category'])
    
    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_post from post order by id_post desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]

    if not myjson['img']:
        return jsonify({"status":5}),200
    img_base64_str= myjson['img']
    img_decode_base64 = base64.b64decode(img_base64_str)
    storage.child("/img/"+str(lastid)).put(img_decode_base64)
    img_url= storage.child("/img/"+str(lastid)).get_url(None)

    id_post= lastid+1
    status= 0
    rating= 0
    create_time= datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    email= get_jwt_identity()
    cur = con.cursor()
    cur.execute("insert into post values (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(id_post,title,content,status,img_url,create_time,getuserid(email),id_category,rating))
    con.commit()
    
    return jsonify({'status':6}),200

#=========== Sủa bài viết =======
# ========== Return status
# 0: not allow
# 1: allow - not exits post
# 2: allow - not contains title
# 3: allow - not contains content
# 4: allow - not contains category
# 5: allow - not exists categroy
# 6: allow - not contains img
# 7: success
@app.route('/post/edit/<int:id_post>',methods=['POST'])
@jwt_required()
def post_edit(id_post):
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    myjson = request.get_json()
    myjson= json.loads(myjson)

    if not check_post_exist(id_post):
        return jsonify({'status':1}),200

    title= myjson['title']
    title=title.strip()
    if not title:
        return jsonify({'status':2}),200

    content= myjson['content']
    content= content.strip()
    if not content: 
        return jsonify({'status':3}),200

    if not myjson['category']:
        return jsonify({"status":4}),200
    if not check_category_exist(int(myjson['category'])):
        return jsonify({"status":5}),200
    id_category= int(myjson['category'])
    
    img_base64_str= myjson['img']
    if not img_base64_str:
        return jsonify({'status':6}),200
    if img_base64_str != "":
        img_decode_base64 = base64.b64decode(img_base64_str)
        storage.child("/img/"+str(id_post)).put(img_decode_base64)    
    img_url= storage.child("/img/"+str(id_post)).get_url(None)

    status= 0
    email= get_jwt_identity()

    cur = con.cursor()
    cur.execute("update post set title=%s,content=%s,status=%s,img=%s,id_category=%s where id_post= %s",(title,content,status,img_url,id_category,id_post))
    con.commit()
    return jsonify({"status":7}),200

# ============ Get post with id ============
# ============ Return status 
# 0: not exists post
@app.route('/post/<int:id_post>')
def get_post(id_post):
    if not check_post_exist(id_post):
        return jsonify({'status':0}),200

    cur = con.cursor()
    cur.execute("SELECT post.title,post.content,post.img,post.create_time,post.rating,account.username from post inner join account on post.create_by= account.id_account where id_post= "+str(id_post))
    rows = cur.fetchall()
    colname=[]
    for i in range(0,6):
        colname.append(cur.description[i][0])

    rtlist=[]
    for row in rows:
        dic={}
        for i in range(0,6):
           dic[colname[i]]=row[i]
        rtlist.append(dic)
    
    cur = con.cursor()
    cur.execute("update post set rating= rating + "+str(1)+" where id_post='"+str(id_post)+"'")
    con.commit()

    js=json.dumps(rtlist,default = myconverter,ensure_ascii=False).encode('utf8')
    return js,200

# =========== Get post with filter sort and select========
# Get api with agrument 
# state --> like where 
# fields --> like select 
# sort --> like order by
# limit --> like limit
# http://127.0.0.1:5000/post?state=status=1&fields=id_post,title,create_time&sort=create_time desc&limit=2
@app.route('/post')
def get_post_filter():
    state=request.args.get('state')
    fields= request.args.get('fields')
    sort= request.args.get('sort')
    limit=request.args.get('limit')

    if limit != None:
        limit=" limit "+str(limit)
    else:
        limit=""

    if sort != None:
        sort=sort.replace(","," ")
        sort=" order by "+sort
    else:
        sort=""

    if state != None:       
        state=state.replace(","," and ")
        state= " where "+state
    else:
        state=""

    if fields != None:
        num_of_fields=len(fields.split(","))
    else:
        num_of_fields=9
        fields=" * "
    
    # sqltest="SELECT "+str(fields)+" from post "+str(state) +str(sort)+str(limit)
    # print(sqltest)
    try:
        cur = con.cursor()
        cur.execute("SELECT "+str(fields)+" from post "+str(state) +str(sort)+str(limit))
        rows = cur.fetchall()
        colname=[]
        for i in range(0,num_of_fields):
            colname.append(cur.description[i][0])

        rtlist=[]
        for row in rows:
            dic={}
            for i in range(0,num_of_fields):
                dic[colname[i]]=row[i]
            rtlist.append(dic)
        js=json.dumps(rtlist,default = myconverter,ensure_ascii=False).encode('utf8')
    except:
        return jsonify({'status':0}),200
    return js,200

# ========= Đăng kí user
# ========= return status+ status code
# 0: success
# 1: invalid username
# 2: invalid email
# 3: invalid password
# 4: email exist
@app.route('/account/reg',methods=['POST'])
def account_reg():
    username= request.headers.get('username')
    email= request.headers.get('email')
    password= request.headers.get('password')
    if not username:
        return jsonify({"status":1}),200
    if not email:
        return jsonify({"status":2}),200
    if not password:
        return jsonify({"status":3}),200
    if checkuser(email):
        return jsonify({"status":4}),200

    # default role
    role= 0
  
    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_account from account order by id_account desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]
    id_account= lastid+1
    # Add account to post
    cur = con.cursor()
    cur.execute("insert into account values (%s,%s,%s,%s,%s)",(id_account,username,password,email,role))
    con.commit()
    return jsonify({"status":0}),200

# ========== Thêm tài khoản=======
# ========== Return status
# 0: not allow
# 1: invalid username
# 2: invalid email
# 3: invalid pasword
# 4: email exist
# 5: invalid role
# 6: sql error
# 7: success
@app.route('/account/add',methods=['POST'])
@jwt_required()
def account_add():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    myjson = request.get_json()
    myjson = json.loads(myjson) 

    email= myjson['email']
    email= email.strip()
    if not email:
        return jsonify({'status':2}),200
    if checkuser(email):
        return jsonify({'status':4}),200

    username = myjson['username']
    username= username.strip()
    if not username:
        return jsonify({'status':1}),200

    password= myjson['password']
    password= password.strip()
    if not password:
        return jsonify({'status':3}),200
    
    if not myjson['role']:
        return jsonify({'status':5}),200
    role= int(myjson['role'])
    
    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_account from account order by id_account desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]
    id_account= lastid+1

    try:
        cur = con.cursor()
        cur.execute("insert into account values (%s,%s,%s,%s,%s)",(id_account,username,password,email,role))
        con.commit()
    except:
        return jsonify({'status':6}),200
    return jsonify({'status':7}),200

# ========== Xóa tài khoản =======
# ========== Return status
# 0: not allow
# 1: not exist account
# 2: SQL error
# 3: Success
@app.route('/account/del/<int:id_account>',methods=['POST'])
@jwt_required()
def account_del(id_account):
    print('ok')
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200
    if not check_account_exist(id_account):
        return jsonify({'status':1}),200
    
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM account WHERE id_account=%s;",(id_account))
        con.commit()
    except:
        return jsonify({'status':2}),200
    return jsonify({'status':3}),200

#=========== Sửa tài khoản =======
#=========== Return status
# 0: not allow
# 1: invalid emaiil
# 2: email exist
# 3: invalid username
# 4: invalid password
# 5: not exist account
# 6: invalid role
# 7: sql error
# 8: success
@app.route('/account/edit',methods=['POST'])
@jwt_required()
def account_edit():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    myjson = request.get_json()
    myjson= json.loads(myjson)

    if not check_account_exist(myjson['id_account']):
        return jsonify({'status':5}),200
    id_account= int(myjson['id_account'])

    email= myjson['email']
    email= email.strip()
    if not email: 
        return jsonify({'status':1}),200
    if checkuser(email):
        return jsonify({'status':2}),200

    username= myjson['username']
    username=username.strip()
    if not username:
        return jsonify({'status':3}),200

    password= myjson['password']
    password= password.strip()
    if not password: 
        return jsonify({'status':4}),200

    if not myjson['role']:
        return jsonify({'status':6}),200
    role= int(myjson['role'])
    
    try:
        cur = con.cursor()
        cur.execute("update account set username=%s,password=%s,email=%s,role=%s where id_account= %s",(username,password,email,role,id_account))
        con.commit()
    except:
        return jsonify({'status':7}),200
    return jsonify({'status':8}),200

# =========== Return all category ==========
@app.route('/category')
def rt_categories():
    cur = con.cursor()
    cur.execute("SELECT * from category")
    rows = cur.fetchall()
    colname=[]
    for i in range(0,4):
        colname.append(cur.description[i][0])
    rtlist=[]
    for row in rows:
        dic={}
        for i in range(0,4):
            dic[colname[i]]=row[i]
        rtlist.append(dic)
    js=json.dumps(rtlist,ensure_ascii=False).encode('utf8')
    return js,200

# ========== Thêm danh mục=======
# 0: not allow ===========
# 1: invalid categrory_name
# 2: invalid level
# 3: invalid id_parent
# 4: not exist id_parent
# 5: SQL error
# 6: Success
@app.route('/category/add',methods=['POST'])
@jwt_required()
def category_add():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    myjson = request.get_json()
    myjson = json.loads(myjson) 

    category_name = myjson['category_name']
    category_name= category_name.strip()
    if not category_name:
        return jsonify({'status':1}),200

    if not myjson['level']:
        return jsonify({'status':2}),200
    level= int(myjson['level'])

    if not myjson['id_parent']:
        return jsonify({'status':3}),200
    id_parent= int(myjson['id_parent'])
    if not check_category_exist(id_parent):
        return jsonify({'status':4}),200

    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_category from category order by id_category desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]
    if not lastid:
        id_category=0
    else:
        id_category= lastid+1

    try:
        cur = con.cursor()
        cur.execute("insert into category values (%s,%s,%s,%s)",(id_category,category_name,id_parent,level))
        con.commit()
    except:
        return jsonify({'status':5}),200
    return jsonify({'status':6}),200

# ========== Xóa danh mục =======
# 0: not allow
# 1: not exist category
# 2: SQL error
# 3: success
@app.route('/category/del/<int:id_category>',methods=['POST'])
@jwt_required()
def category_del(id_category):
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    if not check_category_exist(id_category):
        return jsonify({'status':1}),200
    try:
        cur = con.cursor()
        cur.execute("DELETE FROM category WHERE id_category=%s;",(id_category))
        con.commit()
    except:
        return jsonify({'status':2}),200
    return jsonify({'status':3}),200


#=========== Sủa danh mục =======
# 0: not allow
# 1: invalid category_name
# 2: exist id_category
# 3: invalid id_parent
# 4: not exist id_parent
# 5: invalid level
# 6: SQL error
# 7: Success
@app.route('/category/edit/<int:id_category>',methods=['POST'])
@jwt_required()
def category_edit(id_category):
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    myjson = request.get_json()
    myjson= json.loads(myjson)

    name= myjson['category_name']
    name=name.strip()
    if not name:
        return jsonify({'status':1}),200

    if check_category_exist(id_category):
        return jsonify({'status':2}),200
    id_category= int(myjson['id_category'])

    if not myjson['id_parent']:
        return jsonify({'status':3}),200
    if not check_category_exist(myjson['id_parent']):
        return jsonify({'status':4}),200
    id_parent= int(myjson['id_parent'])

    if not myjson['level']:
        return jsonify({'status':5}),200
    level= int(myjson['level'])
    
    try:
        cur = con.cursor()
        cur.execute("update category set name=%s,id_parent=%s,level=%s where id_category= %s",(name,id_parent,level,id_category))
        con.commit()
    except:
        return jsonify({'status':6}),200
    return jsonify({'status':7}),200

# ========= Get All Account for admin ============
# 0: not allow
# 1: SQL Error
@app.route('/account',methods=['GET'])
@jwt_required()
def get_acc_all():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    try:
        cur = con.cursor()
        cur.execute("SELECT * from account")
        rows = cur.fetchall()
    except:
        return jsonify({'status':1}),200
        
    colname=[]
    for i in range(0,4):
        colname.append(cur.description[i][0])

    rtlist=[]
    for row in rows:
        dic={}
        for i in range(0,4):
           dic[colname[i]]=row[i]
        rtlist.append(dic)

    js=json.dumps(rtlist,default = myconverter,ensure_ascii=False).encode('utf8')
    return js,200

# ========= Get All Account by id============
# 0: not allow
# 1: SQL Error
@app.route('/account/<int:id_account>',methods=['GET'])
@jwt_required()
def get_acc_by_id(id_account):
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return jsonify({'status':0}),200

    try:
        cur = con.cursor()
        cur.execute("SELECT * from account where id_account="+str(id_account))
        rows = cur.fetchall()
    except:
        return jsonify({'status':1}),200
        
    colname=[]
    for i in range(0,4):
        colname.append(cur.description[i][0])

    rtlist=[]
    for row in rows:
        dic={}
        for i in range(0,4):
           dic[colname[i]]=row[i]
        rtlist.append(dic)

    js=json.dumps(rtlist,default = myconverter,ensure_ascii=False).encode('utf8')
    return js,200


@app.route('/test',methods=['GET'])
@jwt_required()
def test():
    email= get_jwt_identity()
    claims = get_jwt()
    return jsonify(claims['role'])

@app.route('/index')
def index1():
    user = get_identity_if_logedin()
    print(user)
    if user==None:
        return render_template('index.html')
    else:
        return jsonify({'Logged':True})

@app.route('/testlogin')
def test_login():
    user = get_identity_if_logedin()
    print(user)
    if user==None:
        return jsonify("No User")
    else:
        return jsonify({'User':user})

@app.route('/2')
def index2():
    cur = con.cursor()
    cur.execute("SELECT * from customer")
    rows = cur.fetchall()
    rtlist=[]
    for row in rows:
        rtlist.append(str(row[0])+" "+row[1])
    return "<h1>Welcome "+rtlist[1]+"!!</h1>"

#test
# @app.route('/test2',methods=['GET'])
# def test2():
#     response=requests.get('http://127.0.0.1:5000/test',headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYxNzAwOTczOCwianRpIjoiMzMxY2U5MjktYmIzZi00ZmE4LWE0ZTItODlmMTQ4NWM4YTdjIiwibmJmIjoxNjE3MDA5NzM4LCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoiYmN2IiwiZXhwIjoxNjE3MDEwNjM4fQ.jUM0ZKGwF7B0rssEdyg0uPWMTWXvUlcrdEeKL_jQLtM'})
#     return response.json()

# app.config['uploadimg']=['/uploadimg/']
# @app.route('/img', methods=["POST"])
# def index3():
#     if request.method == 'POST':
#         if request.files:
#             img= request.files["image"]       
#             # img.save('uploadimg/'+img.filename)
#             storage.child("/img/"+img.filename).put(img)
#             return redirect('/2')

# with open("BANH CAM VINH.PNG", "rb") as img_file:
#     my_string = base64.b64encode(img_file.read())

# imgdata = base64.b64decode(my_string)
# print(type(imgdata))
# filename = 'new_image_2'  # I assume you have a way of picking unique filenames
# # with open(filename, 'wb') as f:
# #     f.write(imgdata)

# storage.child("/img/"+filename).put(imgdata)

# with open("BANH CAM VINH.PNG", "rb") as img_file:
#     my_string = base64.b64encode(img_file.read())

# imgdata = base64.b64decode(my_string)

if __name__ == '__main__':
    app.run()