'''
Created on 14 Oct 2015

@author: mbrandaoca
'''
from app import create_app

from config.dev import *

if __name__ == '__main__':
    app = create_app(SQLALCHEMY_DATABASE_URI)
    app.run(debug=True)