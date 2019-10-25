
import datetime
from flask import Flask

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    date = datetime.datetime.today()
    return f"Hello, World! Today is {date}"
