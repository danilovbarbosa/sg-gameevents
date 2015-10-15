'''
Created on 14 Oct 2015

@author: mbrandaoca
'''
from app import db

class GamingSession(db.Model):
    """"""
    __tablename__ = "gamingsession"
 
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.Boolean)
 
    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.status = 1
        
    def __repr__(self):
        return '<GameSession, Id %r>' % (self.id)