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
# # print(imgdata)
# filename = 'new_image.jpg'  # I assume you have a way of picking unique filenames
# # with open(filename, 'wb') as f:
# #     f.write(imgdata)

# storage.child("/img/"+filename).put(imgdata)

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
def post_add():
    # {"title":"abc","content":"content","category":1,"img":"imgstr"}
    json = request.get_json()

    title= json['title']
    title=title.trip()
    if not title:
        return "Chưa nhập tiêu đề"

    content= json['content']
    content= content.strip()
    if not content:
        return "Chưa nhập nội dung"
    
    # Get last post id
    cur = con.cursor()
    cur.execute("SELECT id_post from post order by id_post desc limit 1")
    rows = cur.fetchall()
    lastid= rows[0][0]

    img_base64_str= json['img']
    img_decode_base64 = base64.b64decode(img_base64_str)
    storage.child("/img/"+str(lastid)).put(img_decode_base64)
    id_post= lastid+1
    status= 0
    rating= 0
    create_time= datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") 

    cur = con.cursor()
    cur.execute("insert into post values (?,?,?,?,?,?,?,?,?)",lastid+1,title,content,status,img,createtime,createby,idcategory,rating)
    con.commit()
    return jsonify("Đã đăng thành công thành công")


# ========== Xóa bài viết =======
#=========== Sủa bài viết =======
# ========== Thêm danh mục=======
# ========== Xóa danh mục =======
#=========== Sủa danh mục =======
# ========== Thêm tài khoản=======
# ========== Xóa tài khoản =======
#=========== Sủa tài khoản =======

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