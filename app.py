from flask import Flask, render_template, jsonify, request, session, redirect, url_for

app = Flask(__name__)

from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
import jwt
import datetime
import hashlib


# client = MongoClient('mongodb://test:test@localhost', 27017)

app = Flask(__name__)
client = MongoClient('localhost', 27017)
db = client.dbhanghae

SECRET_KEY = 'SPARTA'


## HTML 화면 보여주기
@app.route('/')
def homework():
    print("home start")

    question_list = list(db.article.find({}))
    id_list = []

    #id값을 가져올 수 있도록 articles의 ObjectId로 되어있는 _id를 str형식으로 변경한다.
    for item in question_list:
        id_list.append(str(item['_id']))

    for i in range(len(question_list)):
        del question_list[i]['_id']
        question_list[i]['_id'] = id_list[i]

    return render_template('index.html', list=question_list)


## 글쓰기화면 보여주기
@app.route('/write')
def write():
    return render_template('write.html')


## 글쓰기화면 보여주기
@app.route('/login')
def login():
    return render_template('login.html')


## 글쓰기화면 보여주기
@app.route('/api/search', methods=['POST'])
def search():
    words_receive = request.form['words_give']

    find_list = list(db.article.find({'title':{'$regex':words_receive, '$options' : 'i'}},{'_id': False}))

    for i in range(len(find_list)):
        print("find : " + str(find_list[i]))

    return jsonify({'searched_list': find_list})


## 글쓰기화면 보여주기
@app.route('/api/search', methods=['POST'])
def search():
    words_receive = request.form['words_give']

    find_list = list(db.article.find({'title':{'$regex':words_receive, '$options' : 'i'}}))

    id_list = []

    # id값을 가져올 수 있도록 articles의 ObjectId로 되어있는 _id를 str형식으로 변경한다.
    for item in find_list:
        id_list.append(str(item['_id']))

    for i in range(len(find_list)):
        del find_list[i]['_id']
        find_list[i]['_id'] = id_list[i]

    return jsonify({'searched_list': find_list})


## 글쓰기화면 보여주기
@app.route('/api/read')
def read():

    article_id = request.args.get('article_id')
    user_id = request.args.get('user_id')

    target_article = db.article.find_one({'_id': article_id})
    reply_on_article = list(db.reply.find({'article_id', article_id}))

    return render_template('read.html', target_article=target_article, reply_on_article=reply_on_article)


@app.route('/login')
def login():
    return render_template('login.html')

## register 화면 보여주기
@app.route('/registerPage')
def registerPage():
    return render_template('register.html')

## 로그인 API
@app.route('/api/login', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    print(username_receive)
    print(password_receive)

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
        'id': username_receive,
        'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256').decode('utf-8')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})

## id 중복검사
@app.route('/api/idCheck', methods=['POST'])
def idCheck():
    id_receive = request.form['id_give']
    exists = bool(db.user.find_one({"id": id_receive}))
    return jsonify({'result': 'success', 'exists': exists})

## nickname 중복검사
@app.route('/api/nicknameCheck', methods=['POST'])
def nicknameCheck():
    nickname_receive = request.form['nickname_give']
    exists = bool(db.user.find_one({"nickname": nickname_receive}))
    return jsonify({'result': 'success', 'exists': exists})

## 회원가입
@app.route('/api/register', methods=['POST'])
def register():
    id_receive = request.form['id_give']
    pw_receive = request.form['pw_give']
    nickname_receive = request.form['nickname_give']
    email_receive = request.form['email_give']
    zipcode_receive = request.form['zipcode_give']
    address_receive = request.form['address_give']
    detail_receive = request.form['detail_give']
    pw_hash = hashlib.sha256(pw_receive.encode('utf-8')).hexdigest()
    doc = {
        "id": id_receive,
        "password": pw_hash,
        "nickname": nickname_receive,
        "email": email_receive,
        "zipcode": zipcode_receive,
        "address": address_receive,
        "detail": detail_receive,
    }
    db.user.insert_one(doc)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)