from flask import Flask, render_template, request
from sqlite3 import OperationalError
import uuid
import sqlite3

from settings import settings

app = Flask(__name__)

app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')


def check_table():
    create_table = """
        CREATE TABLE IF NOT EXISTS paste(
        URL TEXT NOT NULL PRIMARY KEY,
        LANGUAGE TEXT NOT NULL,
        TITLE TEXT NOT NULL,
        CODE TEXT NOT NULL
        );        
    """

    with sqlite3.connect('paste.db') as conn:
        cursor = conn.cursor()
        try:
            cursor.execute(create_table)
            cursor.close()
        except OperationalError:
            pass


def gen_url():
    valid = False
    uuid_ = None
    while not valid:
        uuid_ = str(uuid.uuid1())[:5]
        with sqlite3.connect('paste.db') as conn:
            sql = "SELECT URL from paste WHERE URL=?"
            cursor = conn.cursor()
            result = cursor.execute(sql, (uuid_,))
            if len(result.fetchall()) == 0:
                valid = True
            cursor.close()
    return uuid_


def save_code(lang, title, code):
    id = gen_url()
    sql = "INSERT INTO paste(URL, LANGUAGE, TITLE, CODE) VALUES (?, ?, ?, ?)"
    with sqlite3.connect('paste.db') as conn:
        cursor = conn.cursor()
        cursor.execute(sql, (id, lang, title, code))


@app.route("/")
def index():
    return render_template('index.pug')


@app.route("/submit", methods=["POST"])
def submit():
    data_dict = request.json

    lang = data_dict['language']
    title = data_dict['title']
    code = data_dict['code']

    save_code(lang, title, code)
    return ""


if __name__ == "__main__":
    check_table()
    app.run(debug=settings["debug"], port=settings["port"])