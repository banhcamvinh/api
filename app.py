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


con = psycopg2.connect(database="d3pbrmjh5hgsb9", user="cuefzkwkvdoncc", password="3b5a03ed19cb22bbb695c2b1763d6a7035e2beb9e97221330a9e209500e1c3b8", host="ec2-52-71-231-37.compute-1.amazonaws.com", port="5432")
app = Flask(__name__)

app.config['JWT_SECRET_KEY']='APISIMPLEAPP'
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=30)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
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

# ============ login==============
# with open("BANH CAM VINH.PNG", "rb") as img_file:
#     my_string = base64.b64encode(img_file.read())

# imgdata = base64.b64decode(my_string)
# print(type(imgdata))
# filename = 'new_image_2'  # I assume you have a way of picking unique filenames
# # with open(filename, 'wb') as f:
# #     f.write(imgdata)

# storage.child("/img/"+filename).put(imgdata)

with open("BANH CAM VINH.PNG", "rb") as img_file:
    my_string = base64.b64encode(img_file.read())
    print(my_string)
imgdata = base64.b64decode(my_string)
# s= imgdata.decode("ascii")
# print(s)

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

def getuserrole(email):
    cur = con.cursor()
    cur.execute("SELECT role from account where email='"+str(email)+"'")
    rows = cur.fetchall()
    return rows[0][0]

def get_identity_if_logedin():
    verify_jwt_in_request(optional=True)
    return get_jwt_identity()

@app.route('/login', methods=['GET'])
def login():
    # email= request.form.get('email')
    # password= request.form.get('password')
    email= request.headers.get('email')
    password= request.headers.get('password')
    if checkuser(email)== False:
        return jsonify({'Login':False},401)
    else:
        if checkpass(email,password)== False:
            return jsonify({'Login':False},401)
        else:
            role= getuserrole(email)
            additional_claims = {"role":role}
            access_token = create_access_token(email, additional_claims=additional_claims)
            refresh_token = create_refresh_token(identity=email)
            resp=jsonify(access_token=access_token,refresh_token=refresh_token,email=email,role=role)
            # resp= jsonify({"access_token":access_token,"refresh_token":refresh_token,"email":email,"role":role})
            set_access_cookies(resp,access_token)
            return resp

@app.route("/logout", methods=["GET"])
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response

@app.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    email = get_jwt_identity()
    role=getuserrole(email)
    additional_claims = {"role":role}
    access_token = create_access_token(email, additional_claims=additional_claims)
    return jsonify(access_token=access_token)

@app.route('/test',methods=['GET'])
@jwt_required()
def test():
    email= get_jwt_identity()
    print(email)
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

@app.route('/2')
def index2():
    cur = con.cursor()
    cur.execute("SELECT * from customer")
    rows = cur.fetchall()
    rtlist=[]
    for row in rows:
        rtlist.append(str(row[0])+" "+row[1])
    return "<h1>Welcome "+rtlist[1]+"!!</h1>"


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
    return js

#============ Get post with filter sort and select========
@app.route('/post')
def rt_n_post_category():
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
    
    cur = con.cursor()
    sqltest="SELECT "+str(fields)+" from post "+str(state) +str(sort)+str(limit)
    print(sqltest)
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
    return js

# ============ Get post with id ============
@app.route('/post/<int:id_post>')
def rt_post(id_post):
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
    js=json.dumps(rtlist,default = myconverter,ensure_ascii=False).encode('utf8')
    return js

# ========== Duyệt bài======
@app.route('/approve/<int:id_post>',methods=['GET'])
@jwt_required()
def rt_approve(id_post):
    myjwt=get_jwt()
    role=myjwt['role']
    # Có quyền chỉnh sửa
    if role == 1:
        cur = con.cursor()
        cur.execute("update post set status=1 where id_post='"+str(id_post)+"'")
        con.commit()
        return jsonify("Đã duyệt thành công")
        pass
    # Không có quyền chỉnh sửa
    elif role == 0:
        return jsonify("Bạn không có quyền chỉnh sửa")
        pass
    # Lỗi không nằm trong quyền trên
    else:
        pass
    return jsonify("Không có role này")


# ========== Thêm bài viết=======
@app.route('/post/add',methods=['POST'])
@jwt_required()
def post_add():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    # {"title":"abc","content":"content","category":1,"img":"imgstr"}
    myjson = request.get_json()
    myjson = json.loads(myjson) 
    title= myjson['title']
    title=title.trip()
    if not title:
        return "Chưa nhập tiêu đề"

    content= myjson['content']
    content= content.strip()
    if not content:
        return "Chưa nhập nội dung"

    id_category= int(myjson['category'])
    
    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_post from post order by id_post desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]

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
    return jsonify("Đã đăng thành công thành công")

# ========== Xóa bài viết =======
@app.route('/post/del/<int:id_post',methods=['POST'])
@jwt_required()
def post_del(id_post):
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    cur = con.cursor()
    cur.execute("DELETE FROM post WHERE id_post=%s;",(id_post))
    con.commit()
    return jsonify("Đã đăng thành công thành công")
    
#=========== Sủa bài viết =======
@app.route('/post/edit',methods=['POST'])
@jwt_required()
def post_edit():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    myjson = request.get_json()
    myjson= json.loads(myjson)
    title= myjson['title']
    title=title.trip()
    if not title:
        return "Chưa nhập tiêu đề"

    content= myjson['content']
    content= content.strip()
    if not content: 
        return "Chưa nhập nội dung"

    id_category= int(myjson['category'])
    
    id_post= int(myjson['post_id'])

    img_base64_str= myjson['img']
    if img_base64_str != "":
        img_decode_base64 = base64.b64decode(img_base64_str)
        storage.child("/img/"+str(id_post)).put(img_decode_base64)    
    img_url= storage.child("/img/"+str(id_post)).get_url(None)

    status= 0
    email= get_jwt_identity()

    cur = con.cursor()
    cur.execute("update post set title=%s,content=%s,status=%s,img=%s,id_category=%s where id_post= %s",(title,content,status,img_url,id_category,id_post))
    con.commit()
    return jsonify("Đã edit thành công")

# ========== Thêm danh mục=======
@app.route('/category/add',methods=['POST'])
@jwt_required()
def category_add():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    myjson = request.get_json()
    myjson = json.loads(myjson) 
    category_name = myjson['category_name']
    category_name= category_name.trip()
    if not category_name:
        return "Chưa nhập tên"

    level= int(myjson['level'])

    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_category from category order by id_category desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]
    id_category= lastid+1

    id_parent= myjson['id_parent']

    cur = con.cursor()
    cur.execute("insert into category values (%s,%s,%s,%s)",(id_category,category_name,id_parent,level))
    con.commit()
    return jsonify("Đã đăng thành công thành công")

# ========== Xóa danh mục =======
@app.route('/category/del/<int:id_category',methods=['POST'])
@jwt_required()
def category_del(id_category):
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    cur = con.cursor()
    cur.execute("DELETE FROM category WHERE id_category=%s;",(id_category))
    con.commit()
    return jsonify("Đã xóa thành công thành công")
#=========== Sủa danh mục =======
@app.route('/category/edit',methods=['POST'])
@jwt_required()
def category_edit():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    myjson = request.get_json()
    myjson= json.loads(myjson)

    name= myjson['name']
    name=name.trip()
    if not name:
        return "Chưa nhập tiêu đề"
    id_category= int(myjson['id_category'])
    id_parent= int(myjson['id_parent'])
    level= int(myjson['level'])
    
    cur = con.cursor()
    cur.execute("update category set name=%s,id_parent=%s,level=%s where id_category= %s",(name,id_parent,level,id_category))
    con.commit()
    return jsonify("Đã edit thành công")

# ========== Thêm tài khoản=======
@app.route('/account/add',methods=['POST'])
@jwt_required()
def account_add():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    myjson = request.get_json()
    myjson = json.loads(myjson) 

    username = myjson['username']
    username= username.trip()
    if not username:
        return "Chưa nhập tên"

    password= myjson['password']
    email= myjson['email']
    role= int(myjson['role'])
    
    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_account from account order by id_account desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]
    id_account= lastid+1

    cur = con.cursor()
    cur.execute("insert into account values (%s,%s,%s,%s,%s)",(id_account,username,password,email,role))
    con.commit()
    return jsonify("Đã đăng thành công thành công")
# ========== Xóa tài khoản =======
@app.route('/account/del/<int:id_account',methods=['POST'])
@jwt_required()
def account_del(id_account):
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    cur = con.cursor()
    cur.execute("DELETE FROM account WHERE id_account=%s;",(id_account))
    con.commit()
    return jsonify("Đã đăng thành công thành công")
#=========== Sủa tài khoản =======
@app.route('/account/edit',methods=['POST'])
@jwt_required()
def account_edit():
    myjwt=get_jwt()
    role=myjwt['role']
    if role == 0:
        return "Bạn không có quyền truy cấp"

    myjson = request.get_json()
    myjson= json.loads(myjson)

    username= myjson['username']
    username=username.trip()
    if not username:
        return "Chưa nhập tiêu đề"

    password= myjson['password']
    password= password.strip()
    if not password: 
        return "Chưa nhập nội dung"
    
    email= myjson['email']
    email= email.strip()
    if not email: 
        return "Chưa nhập nội dung"

    id_account= int(myjson['id_account'])
    role= int(myjson['role'])
    
    cur = con.cursor()
    cur.execute("update account set username=%s,password=%s,email=%s,role=%s where id_account= %s",(username,password,email,role,id_account))
    con.commit()
    return jsonify("Đã edit thành công")

# @app.route('/test2',methods=['GET'])
# def test2():
#     response=requests.get('http://127.0.0.1:5000/test',headers={'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYxNzAwOTczOCwianRpIjoiMzMxY2U5MjktYmIzZi00ZmE4LWE0ZTItODlmMTQ4NWM4YTdjIiwibmJmIjoxNjE3MDA5NzM4LCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoiYmN2IiwiZXhwIjoxNjE3MDEwNjM4fQ.jUM0ZKGwF7B0rssEdyg0uPWMTWXvUlcrdEeKL_jQLtM'})
#     return response.json()

# cur = con.cursor()
# cur.execute("SELECT * from customer")
# rows = cur.fetchall()
# for row in rows:
#     print("ID =", row[0])
#     print("Name =", row[1])
# con.close()


# app.config['uploadimg']=['/uploadimg/']
# @app.route('/img', methods=["POST"])
# def index3():
#     if request.method == 'POST':
#         if request.files:
#             img= request.files["image"]       
#             # img.save('uploadimg/'+img.filename)
#             storage.child("/img/"+img.filename).put(img)
#             return redirect('/2')


if __name__ == '__main__':
    app.run()