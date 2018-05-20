from flask import abort, Flask, render_template, request
from sqlite3 import OperationalError
import uuid
import sqlite3

from settings import settings

app = Flask(__name__)

app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')


def replacelast(line: str, delimiter: str, replace: str, count: int) -> str:
    return replace.join(line.rsplit(delimiter, count))


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
    return id

@app.route("/")
def index():
    return render_template('index.pug')


@app.route("/submit", methods=["POST"])
def submit():
    data = request.data.decode('utf-8').replace("\n", "\\n")
    split_data = replacelast(data.replace("{", "", 1), "}", "", 1).split(", ", 2)

    lang = replacelast(split_data[0].split(": ", 1)[1].replace("\"", "", 1), "\"", "", 1)
    title = replacelast(split_data[1].split(": ", 1)[1].replace("\"", "", 1), "\"", "", 1)
    code = replacelast(split_data[2].split(": ", 1)[1].replace("\"", "", 1), "\"", "", 1)

    id = save_code(lang, title, code)
    print("saved")
    return "http://" + request.base_url.split("//", 1)[1].split("/", 1)[0] + "/" + id


@app.route("/<url>")
def read(url):
    sql = "SELECT * from paste WHERE URL=?"
    with sqlite3.connect('paste.db') as conn:
        cursor = conn.cursor()
        result = cursor.execute(sql, (url,))
        data = result.fetchall()[0]
        lang_ = data[1]
        name_ = data[2]
        code_ = data[3].replace("\\n", "\n")
        return render_template('code.pug', lang=lang_, name=name_, code=code_)
    return abort(404)

if __name__ == "__main__":
    check_table()
    app.run(debug=settings["debug"], port=settings["port"])