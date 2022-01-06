# import required modules
from flask import abort, Flask, render_template, request
from sqlite3 import OperationalError
import uuid
import sqlite3

# import settings
from settings import settings

# get flask instance
app = Flask(__name__)

# add support for pug html
app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')


def replacelast(line: str, delimiter: str, replace: str, count: int) -> str:
    """
    Replace the last occurance of a string in another string

    line: the line to be modified
    delimeter: the character or string to be replaced
    replace: what to replace with
    count: how many occurances to split
    """

    # line.rsplit() used to split the line <count> amount of times from the end of the string at the provided delimiter
    # str.join() used to join the list that rsplit creates using the provided replace string as the connecting value
    return replace.join(line.rsplit(delimiter, count))


def create_table_if_not_exists():
    """
    Create a table in the sqlite database if it doesn't already exist
    """

    # sql query
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
    """get a unique id for the paste"""
    
    # is the generated id valid
    valid = False
    # unique id
    uuid_ = None
    # loop until a valid uuid is created
    while not valid:
        # get last 5 characters of a random uuid from uuid module using uuid1 function
        # uuid1() generates a uuid based on host ID, sequence number, and current time
        uuid_ = str(uuid.uuid1())[:5]
        
        # check if the uuid is actually unique
        # open the database into conn variable
        with sqlite3.connect('paste.db') as conn:
            # query to find any matches for the uuid
            sql = "SELECT URL from paste WHERE URL=?"
            # get instance of db cursor
            cursor = conn.cursor()
            # execute the query
            result = cursor.execute(sql, (uuid_,))
            # check if any results were found
            if len(result.fetchall()) == 0:
                # nothing found
                valid = True
            # close the connection
            cursor.close()
    # return the unique id
    return uuid_


def save_code(lang, title, code):
    """
    save a paste
    
    lang: the language used
    title: title of the paste
    code: code within the paste
    """

    # get a unique id
    id = gen_url()
    # sql query to save data with placeholders to avoid injection
    sql = "INSERT INTO paste(URL, LANGUAGE, TITLE, CODE) VALUES (?, ?, ?, ?)"
    # get a connection into conn variable
    with sqlite3.connect('paste.db') as conn:
        # get instance of the cursor
        cursor = conn.cursor()
        # execute the query with placeholder values as a tuple
        cursor.execute(sql, (id, lang, title, code))
    # return the id to the paste
    return id


# index for flask
@app.route("/")
def index():
    # render the index template passing the url for the site as a variable
    return render_template('index.pug', url=settings["host"])


# paste submission, can only be accessed via POST request
# if I were to do this again I'd read the data as a dictionary rather than manually parsing the json data
@app.route("/submit", methods=["POST"])
def submit():
    # get the data from the request, escaping new line delimiters
    data = request.data.decode('utf-8').replace("\n", "\\n")
    # remove the surrounding braces from the data
    split_data = replacelast(data.replace("{", "", 1), "}", "", 1).split(", ", 2)
    # get the language used
    lang = replacelast(split_data[0].split(": ", 1)[1].replace("\"", "", 1), "\"", "", 1)
    # get the title used
    title = replacelast(split_data[1].split(": ", 1)[1].replace("\"", "", 1), "\"", "", 1)
    # get the actual code
    code = replacelast(split_data[2].split(": ", 1)[1].replace("\"", "", 1), "\"", "", 1)

    # ssave the paste
    id = save_code(lang, title, code)
    # output to console
    print("saved")
    # return url to the paste
    return settings["host"] + "/" + id


# route for a paste
@app.route("/<url>")
def read(url):
    # ensure id is 5 characters long
    if len(url) == 5:
        # query to get paste from DB
        sql = "SELECT * from paste WHERE URL=?"
        # open db into conn variable
        with sqlite3.connect('paste.db') as conn:
            # get cursor instance
            cursor = conn.cursor()
            # execute the query with placeholder values, keeping the result in "result" variable
            result = cursor.execute(sql, (url,))
            # get data from the result
            data = result.fetchall()[0]
            # get the language of the paste
            lang_ = data[1]
            # get the name of the paste
            name_ = data[2]
            # get the contents of the paste
            code_ = data[3].replace("\\n", "\n")
            # render template for the webpage
            return render_template('code.pug', lang=lang_, name=name_, code=code_, url=settings["host"])
    # invalid id, return 404 instead
    return abort(404)


if __name__ == "__main__":
    create_table_if_not_exists()
    app.run(debug=settings["debug"], port=settings["port"])