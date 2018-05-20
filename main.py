from flask import Flask, render_template, request

from settings import settings

app = Flask(__name__)

app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')


@app.route("/")
def index():
    return render_template('index.pug')


@app.route("/submit", methods=["POST"])
def submit():
    json_data = request.json
    print(json_data)
    # TODO: save data to database
    return ""


if __name__ == "__main__":
    app.run(debug=settings["debug"], port=settings["port"])