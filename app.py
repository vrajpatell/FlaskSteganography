from flask import Flask, render_template, redirect, url_for, request, session
from forms import encodeForm, decodeForm
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
from PIL import Image
import secrets
from alg_apply import original_text, enc_alg, dec_alg

import re

# from flask.ext.session import Session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'QWERTYU12345673ERFGHBNTRDGFCN6RUFKJV'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = 'your password'
app.config['MYSQL_DB'] = 'login'

mysql = MySQL(app)


def save_image(im):
    _, ext = os.path.splitext(im.filename)
    fn = secrets.token_hex(4) + '_' + 'org' + ext
    pic_path = os.path.join(app.root_path, "static/org_pic", fn)
    i = Image.open(im)
    i.save(pic_path)
    print('saved')
    # enc_alg(pic_path)
    # print('Return password: ', enc_alg(pic_path))
    return pic_path


@app.route('/encode', methods=['GET', 'POST'])
def encode():
    title = '-encode'
    form = encodeForm()
    if form.is_submitted():
        print("submitted")
    # return redirect(url_for('encode'))
    if form.validate_on_submit():
        print('ok done!')
        pic = form.picture.data
        try:
            pwd, img = enc_alg(save_image(pic))
            pd_ret = str(pwd)
            im_ret = str(img).split('/')[-1]

            print('***************', str(img).split('/')[-1
            ])
            return render_template('dl_page.html', pd_ret=pd_ret, im_ret=im_ret)
        except:
            return render_template('retrieve_msg.html', message='error')
            pass
    else:
        print('not done')
    return render_template('encode.html', title=title, form=form)


def save_deImage(org, enc):
    # print(org.filename, enc.filename)
    _, ext_o = os.path.splitext(org.filename)
    _, ext_e = os.path.splitext(enc.filename)
    sec = secrets.token_hex(4)
    fn_org = sec + '_' + 'd' + '_' + 'org' + ext_o
    fn_enc = sec + '_' + 'd' + '_' + 'enc' + ext_e
    pic_path_o = os.path.join(app.root_path, "static/de_org_pic", fn_org)
    pic_path_e = os.path.join(app.root_path, "static/de_enc_pic", fn_enc)
    im_o = Image.open(org).save(pic_path_o)
    im_e = Image.open(enc).save(pic_path_e)
    return pic_path_o, pic_path_e


@app.route('/decode', methods=['GET', 'POST'])
def decode():
    title = '-decode'
    form = decodeForm()
    if form.is_submitted():
        print('decode form submitted')
    if form.validate_on_submit():
        print('decode form ok done!')
        org_pic = form.picture_o.data
        enc_pic = form.picture_e.data
        # save_deImage(org_pic, enc_pic)
        pic_path_o, pic_path_e = save_deImage(org_pic, enc_pic)
        message = str(dec_alg(pic_path_o, pic_path_e))
        return render_template('retrieve_msg.html', message=message)
    else:
        print('not done')

    return render_template('decode.html', title=title, form=form)


# def home():
#	return render_template('index.html')
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s AND password = % s', (username, password,))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return render_template('index.html', msg=msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html', msg=msg)


@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM accounts WHERE username = % s', (username,))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO accounts VALUES (NULL, % s, % s, % s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('register.html', msg=msg)


@app.route('/home')
def home():
    return render_template('index.html')


if __name__ == '__main__':
    # app.run(debug = True)
    app.run()
