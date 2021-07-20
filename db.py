from flask_sqlalchemy import SQLAlchemy 
import requests
from secret import API_KEY


db = SQLAlchemy()

def connect_db(app):
    db.app = app
    db.init_app(app)

