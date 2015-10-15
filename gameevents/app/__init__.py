'''
Created on 14 Oct 2015

@author: mbrandaoca
'''
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from app import apiviews, controller

