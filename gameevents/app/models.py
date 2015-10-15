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
    
    gameevents = db.relationship("GameEvent", backref="gamingsession")
 
    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        self.status = True
        
    def __eq__(self, other):
        return self.id == other.id and self.status == other.status
    
class GameEvent(db.Model):
    """"""
    __tablename__ = "gameevent"
 
    id = db.Column(db.Integer, primary_key=True)
    gameevent = db.Column(db.String)    

    gamingsession_id = db.Column(db.Integer, db.ForeignKey('gamingsession.id'))
 
    #----------------------------------------------------------------------
    def __init__(self, gamingsessionid, gameevent):
        """"""
        self.gamingsession_id = gamingsessionid
        self.gameevent = gameevent
        
    def __repr__(self):
        return '<GameEvent. id: %s; gamingsession_id: %s; gameevent: %s [...]>' % (self.id, self.gamingsession_id, self.gameevent[:100])
    
    def __eq__(self, other):
        return self.id == other.id and self.gameevent == other.gameevent and self.gamingsession_id == other.gamingsession_id