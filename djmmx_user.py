#-*- coding: UTF-8 -*- 
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from datetime import timedelta
import re
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

def connect_db():
    host = 'localhost'
    db = 'djmmxuser'
    port = 3306
    user = 'root'
    pw = ''
    try:
        import sae.const
        host = sae.const.MYSQL_HOST
        db = sae.const.MYSQL_DB
        port = int(sae.const.MYSQL_PORT)
        user = sae.const.MYSQL_USER
        pw = sae.const.MYSQL_PASS
    except ImportError:
        pass
    return MySQLdb.connect(host=host,port=port,user=user,passwd=pw,db=db,charset='utf8')

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db

def error_msg(e, phone_number, username):
    if e[0] == 1062:
        return u'已存在手机号为%s的用户：%s' %(phone_number, username)
    return u'数据库错误！'
  
# DATABASE=os.path.join(app.root_path, 'flaskr.db'),
# DEBUG=True,
SECRET_KEY='development key'
USERNAME=u'linengxing'
PASSWORD=u'TYXR736'

app = Flask(__name__)  
app.config.from_object(__name__)

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=60)
 
@app.route('/login', methods=['GET', 'POST'])  
def login():  
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = u'用户名错误！'
        elif request.form['password'] != app.config['PASSWORD']:
            error = u'密码错误！'
        else:
            session['logged_in'] = True
            flash(u'登陆成功！')
            return redirect(url_for('show_users'))
    return render_template('login.html', error=error)

@app.route('/')
def show_users():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db = get_db()
    cursor = db.cursor()
    cursor.execute('select name, wx_discount, credit, phone_number from users order by id desc')
    users = cursor.fetchall()
    return render_template('show_users.html', users=users)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash(u'注销成功')
    return redirect(url_for('show_users'))
      

@app.route('/add', methods=['POST', 'GET'])
def add_user():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        username = request.form['name']
        phone_number = request.form['phone_number']
        username_patt = re.compile(ur"(^[\u4e00-\u9fa5]{2,}$)")
        phone_number_patt = re.compile(ur"^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$")
        if username == u'姓名':
            error = u'请输入客户姓名！'
        elif phone_number == u'手机号':
            error = u'请输入客户手机号！'
        elif not username_patt.match(username):
            error = u'姓名必须为2个以上汉字！'
        elif not phone_number_patt.match(phone_number):
            error = u'手机号码格式非法！'
        else:
            db = get_db()
            cursor = db.cursor()
            try:
                cursor.execute("insert into users(name, phone_number) values ('%s', '%s')" %(request.form['name'].encode('utf-8'), request.form['phone_number'].encode('utf-8')))
                db.commit()
                flash(u'用户添加成功！')
                return redirect(url_for('show_users'))
            except MySQLdb.Error as e:
                db.rollback()
                cursor.execute("select name from users where phone_number=('%s')" %(phone_number.decode('utf-8')))
                user = cursor.fetchall()
                error = error_msg(e, phone_number, user[0][0])
            finally:
                cursor.close()
                db.close()

    return render_template('add_user.html', error=error)

@app.route('/update/<phone_number>', methods=['POST', 'GET'])
def update_user(phone_number):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    error = None
    if request.method == 'POST':
        if request.form.get('wx_discount') == u'auto':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("update users set wx_discount=mod(wx_discount+1,2) where phone_number=('%s')" %(phone_number.decode('utf-8')))
            db.commit()
            flash(u'优惠信息已更新！')
            return redirect(url_for('show_users'))
        if 'delt_credit' in request.form:
            operand = request.form['delt_credit']
            patt = re.compile(r'^[1-9][0-9]*$')
            if not patt.match(operand):
                flash(u'请输入一个正整数！')
                return redirect(url_for('show_users'))
            operator = '+' if request.form['is_positive'] == u'true' else '-'
            db = get_db()
            cursor = db.cursor()
            cursor.execute("update users set credit=greatest(credit%s%d, 0) where phone_number=('%s')" %(operator, int(operand), phone_number.decode('utf-8')))
            db.commit()
            flash(u'积分已更新！')
            return redirect(url_for('show_users'))
        if 'name' in request.form:
            username_patt = re.compile(ur"(^[\u4e00-\u9fa5]{2,}$)")
            if not username_patt.match(request.form['name']):
                flash(u'姓名必须为2个以上汉字！')
                return redirect(url_for('show_users'))
            db = get_db()
            cursor = db.cursor()
            cursor.execute("update users set name='%s' where phone_number=('%s')" %(request.form['name'].encode('utf-8'), phone_number.decode('utf-8')))
            db.commit()
            flash(u'姓名已更新！')
            return redirect(url_for('show_users'))
        if 'phone_number' in request.form:
            phone_number_patt = re.compile(ur"^(13[0-9]|15[012356789]|17[678]|18[0-9]|14[57])[0-9]{8}$")
            if not phone_number_patt.match(request.form['phone_number']):
                flash(u'手机号码格式非法！')
                return redirect(url_for('show_users'))
            db = get_db()
            cursor = db.cursor()
            try:
                cursor.execute("update users set phone_number='%s' where phone_number=('%s')" %(request.form['phone_number'].encode('utf-8'), phone_number.decode('utf-8')))
                db.commit()
                flash(u'手机号已更新！')
            except MySQLdb.Error as e:
                db.rollback()
                cursor.execute("select name from users where phone_number=('%s')" %(request.form['phone_number'].decode('utf-8')))
                user = cursor.fetchall()
                flash(error_msg(e, phone_number, user[0][0]))
            finally:
                cursor.close()
                db.close()
                return redirect(url_for('show_users'))

    abort(401)

if __name__ == '__main__':  
    app.run(host='0.0.0.0')
