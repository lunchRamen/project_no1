import os
import csv
import dotenv

from flask import Flask,session
from flask_login import LoginManager
from db_connect import db
from flask_wtf.csrf import CSRFProtect
from datetime import date, datetime,timedelta
from models import BookInfo


app = Flask(__name__)
dotenv.load_dotenv('.env')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URI')
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(seconds=5)
app.secret_key = os.environ.get('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
#csrf = CSRFProtect()
#csrf.init_app(app)

db.init_app(app)

from . import auth
app.register_blueprint(auth.bp)

from . import main
app.register_blueprint(main.bp)

@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=1)

if __name__ == '__main__':
    app.run('0.0.0.0', 80, debug=True)

