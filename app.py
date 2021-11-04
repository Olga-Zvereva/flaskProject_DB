from flask import Flask, render_template, request, url_for, g, flash, abort
import os
import sqlite3 as sqlite

#создадим конфигурацию
from FDataBase import FDataBase

DATABASE = '/tmp/flsite.db'
DEBUG =True
SECRET_KEY = "qwertyuiasdfg23455dfgh"

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db'))) #переопределяем БД

def connect_db(): #создание соединения с БД
    conn = sqlite.connect(app.config["DATABASE"])
    conn.row_factory = sqlite.Row
#The line of code assigning sqlite3.Row to the row_factory of connection creates what some
#people call a 'dictionary cursor', - instead of tuples it starts returning 'dictionary' rows after
#fetchall or fetchone.
    return conn

def create_db(): #создание БД
    conn = connect_db()
    cursor = conn.cursor()
    with app.open_resource('create.sql', mode='r') as f: #чтение операторов создания таблиц из файла
         cursor.executescript(f.read())
    conn.commit()
    conn.close()

def get_db(): # установление связи с БД
    if not hasattr(g, 'link_db'): #g - глобальная переменная в контексте приложения
        g.link_db = connect_db()
    return g.link_db

@app.teardown_appcontext
def close_db(error):
    '''Закрыть соединение с БД, если оно было установлено'''
    if hasattr(g, 'link_db'):
        g.link_db.close()

@app.route('/')
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('index.html',  menu=dbase.getMenu(), posts=dbase.getPostTitle())

@app.route('/add_post', methods=["GET", "POST"])
def addpost():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == "POST":
        print(request.form["name"])
        request.form["post"]
        if len(request.form["name"])>4 and len(request.form["post"])>10:
            res = dbase.addPost(request.form["name"], request.form["post"], request.form["url"])
            if not res:
                flash ("Ошибка добавления поста...", category="error")
            else:
                flash("Пост добавлен успешно!", category="success")
        else:
            flash("Ошибка добавления поста", category="error")
    return render_template('post.html',  menu =  dbase.getMenu(), title = "Добавление статьи")

@app.route("/post/<alias>")
def show_post(alias):
    db = get_db()
    dbase = FDataBase(db)
    title1, post = dbase.getPost(alias)

    if not title1:
        abort(404)

    return render_template('post_show.html', menu =dbase.getMenu(), title=title1, post=post)


if __name__ == '__main__':
    app.run()
