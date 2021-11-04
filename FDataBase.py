import math
import re
import sqlite3
import time

from flask import flash, url_for


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql_com = 'SELECT * from mainmenu'
        try:
            self.__cur.execute(sql_com)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print("DB ERROR!")
        return []

    def addPost(self, title, post, url):
        try:
            #проверка, была ли статья ранее загружена (уже есть такоц url)
            self.__cur.execute(f"SELECT COUNT()  FROM posts WHERE url LIKE '{url}' ")
            res = self.__cur.fetchone()
            if res[0] > 0:
                print(f"Такая запись есть в базе")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?) ", (title, post, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            flash("Ошибка добавления поста в БД - " + str(e))
            return False
        return True

    def getPost(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM posts WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                # путь, где находятся картинки
                base = url_for("static", filename = "Images_html")
                print(f"base -> {base}")
                # поиск всех тегов img и замена в них путей к файлам картинок
                text = re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)\s*?>",
                       "\\g<tag>"+base+"/\g<url>", res['text'])
                return res['title'], text
        except sqlite3.Error as e:
            print("Ошибка поиска поста - " + str(e))
            return False, False


    def getPostTitle(self):
        try:
            self.__cur.execute("SELECT id, title, url, text FROM posts ORDER BY time DESC ")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка БД - " + str(e))
            return []




