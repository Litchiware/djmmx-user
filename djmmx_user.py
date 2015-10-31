#-*- coding: UTF-8 -*- 
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
import MySQLdb

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
    return MySQLdb.connect(host=host,port=port,user=user,passwd=pw,db=db)

def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db
  
# DATABASE=os.path.join(app.root_path, 'flaskr.db'),
# DEBUG=True,
SECRET_KEY='development key'
USERNAME=u'admin'
PASSWORD=u'default'

app = Flask(__name__)  
app.config.from_object(__name__)
app.debug=True
 
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
    cursor.execute('select wx_id, name, wx_discount, credit from users order by id desc')
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
        abort(401)
    error = None
    if request.method == 'POST':
        if request.form['wx_id'] == u'微信号':
            error = u'请输入微信号！'
        elif request.form['name'] == u'姓名':
            error = u'请输入客户姓名！'
        else:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("insert into users(wx_id, name) values ('%s', '%s')" %(request.form['wx_id'].encode('utf-8'), request.form['name'].encode('utf-8')))
            db.commit()
            flash(u'用户添加成功！')
            return redirect(url_for('show_users'))
    return render_template('add_user.html', error=error)

@app.route('/update/<wx_id>', methods=['POST', 'GET'])
def update_user(wx_id):
    if request.method == 'POST':
        if request.form.get('wx_discount') == u'auto':
            db = get_db()
            cursor = db.cursor()
            cursor.execute("update users set wx_discount=mod(wx_discount+1,2) where wx_id=('%s')" %(wx_id.decode('utf-8')))
            db.commit()
            flash(u'转发优惠！')
            return redirect(url_for('show_users'))
        if 'delt_credit' in request.form:
            db = get_db()
            cursor = db.cursor()
            operator = '+' if request.form['is_positive'] == u'true' else '-'
            cursor.execute("update users set credit=credit%s%d where wx_id=('%s')" %(operator, int(request.form.get('delt_credit')), wx_id.decode('utf-8')))
            db.commit()
            flash(u'积分已更新！')
            return redirect(url_for('show_users'))

    abort(401)

if __name__ == '__main__':  
    app.run(host='0.0.0.0')
