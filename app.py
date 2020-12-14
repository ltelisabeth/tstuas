from flask import Flask, request, jsonify, redirect, url_for, session, render_template
from flaskext.mysql import MySQL
from flask_oauth import OAuth
import logging
from logging.handlers import RotatingFileHandler
import time
# library request buat dapatin bodynya gitu
# ngereturn json, biar hasilnya itu bagus

oauth = OAuth()
app = Flask(__name__)
mysql = MySQL()
app.secret_key = 'secretkey'
app.secret_key = 'secretkey'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'tst_uas'
app.config['MYSQL_DATABASE_HOST'] = '172.24.0.2'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

mysql.init_app(app)
google = oauth.remote_app('google',
                          base_url='https://www.google.com/accounts/',
                          authorize_url='https://accounts.google.com/o/oauth2/auth',
                          request_token_url=None,
                          request_token_params={'scope': 'https://www.googleapis.com/auth/userinfo.email',
                                                'response_type': 'code'},
                          access_token_url='https://accounts.google.com/o/oauth2/token',
                          access_token_method='POST',
                          access_token_params={'grant_type': 'authorization_code'},
                          consumer_key='284463975146-mtm76jl4t7n31t11tn1qqcric26hspfi.apps.googleusercontent.com',
                          consumer_secret='xvV2f5t_2dDJdW7R8dpPPK9M')

# yang penting ada routenya
# HTTP request method: GET, POST, PUT, DELETE
# umumnya dipake yang GET POST
@app.route('/')
def landing():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ 'Akses Landing Page')
    return render_template('index.html')

@app.route('/home')
def index():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ 'Akses Home Page')
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login')
def login():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ 'Akses Login Page')
    callback=url_for('authorized', _external=True)
    return google.authorize(callback=callback)

@app.route('/authorized')
@google.authorized_handler
def authorized(resp):
    access_token = resp['access_token']
    # session['access_token'] = access_token, ''
    print(access_token)
    session['access_token'] = access_token, ''
    return redirect(url_for('index'))


#GET, POST, PUT, DELETE http req method
@app.route('/book', methods=['GET'])
def get_user():
    # data = ['alya', 'nomi', 'abeth']
    # users = {
    #     'status': 'sukses',
    #     'message': 'ini hasilnya',
    #     'data': data
    #     # sabi diganti apapun
    # }

    # skrg from database
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ 'Akses Book Info')
    conn = mysql.connect()
    cursor = conn.cursor()
    query = 'SELECT * FROM book'

    cursor.execute(query)
    result = cursor.fetchall()

    result_baru = []

    for book in result:
        akun_baru = {
            'id': book[0],
            'title': book[1],
            'author': book[2],
            'totalpages': book[3],
            'type': book[4],
            'published': book[5],
        }
        result_baru.append(akun_baru)
    #return(render_template('show.html'))
    return {'hasil': result_baru}

@app.route('/newBook', methods=['POST', 'GET'])
def insert_user():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ 'Akses Add New Book Page')
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        return render_template('add.html')
    elif request.method == 'POST':
        conn = mysql.connect()
        cursor = conn.cursor()
        title = request.form['title']
        author = request.form['author']
        totalpages = request.form['totalpages']
        type = request.form['type']
        published = request.form['published']

        query = 'INSERT INTO book (title, author, totalpages, type, published) VALUES (%s, %s, %s, %s, %s)'
        data = (title, author, totalpages, type, published)

        cursor.execute(query, data)
        conn.commit()
        conn.close()

        result = {
            'title': title,
            'author': author,
            'totalpages': totalpages,
            'type': type,
            'published': published
        }
        return {'hasil': result}

@app.route('/details', methods=['PUT', 'GET'])
def update_user():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ 'Akses Update Book Page')
    # data = ['alya', 'nomi', 'abeth']
    # users = {
    #     'status': 'sukses',
    #     'message': 'ini hasilnya',
    #     'data': data
    #     # sabi diganti apapun
    # }

    # skrg from database
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        return render_template('update.html')
    elif request.method == 'PUT':
        conn = mysql.connect()
        cursor = conn.cursor()
        id = request.form['id']
        title = request.form['title']
        
        # cursor buat melakukan perintah2
        query = 'UPDATE book SET title = %s WHERE id = %s'
        data = (title, id)

        cursor.execute(query, data)
        conn.commit()
        conn.close()

        result = {
            'Data berhasil diubah'
        }
        # dari mysql hasilnya langsung list, tapi listnya double
        return render_template('update.html')
        #return {'hasil': result}
        # list: data[0] data[1]
        # json/dictionary: data['nama']

@app.route('/delete',methods=['DELETE', 'GET'])
def delete_akun():
    app.logger.error(time.strftime('%A %B, %d %Y %H:%M:%S')+ 'Akses Delete Book Page')
    # skrg from database
    access_token = session.get('access_token')
    if access_token is None:
        return redirect(url_for('login'))
    if request.method == 'GET':
        conn = mysql.connect()
        cursor = conn.cursor()
        return render_template('delete.html')
    elif request.method == 'DELETE':
        conn = mysql.connect()
        cursor = conn.cursor()
        id = request.form['id']
        query = 'DELETE FROM book WHERE id = %s'

        cursor.execute(query,(id))
        conn.commit()
        conn.close()

        result = [{
                'status': 204,
                'message': "Success Delete"
        }]
        return render_template('delete.html')
        #return jsonify(result)

if __name__ == "__main__":
    handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(host='0.0.0.0')
