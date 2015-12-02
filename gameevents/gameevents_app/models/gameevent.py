''''''

from uuid import UUID
import OpenSSL
import simplejson

from flask import url_for

from ..extensions import db

    
class GameEvent(db.Model):
    '''
    Models 'gameevent' table in the database.
    
    :param str sessionid: sessionid to which the gameevent belongs
    :param str gameevent: JSON formatted gameevent, serialized as string
  
    '''
    __tablename__ = "gameevent"

    #: (uuid) internal ID of the event
    id = db.Column(db.String(36), primary_key=True)
    #: long text, formatted as JSON (or serialized dict)
    gameevent = db.Column(db.UnicodeText())
    #: (uuid) foreign key to Session table 
    session_id = db.Column(db.String(36), db.ForeignKey('session.id'))
 
    #----------------------------------------------------------------------
    def __init__(self, sessionid, gameevent):
        self.id = UUID(bytes = OpenSSL.rand.bytes(16)).hex
        self.session_id = sessionid
        #self.gameevent = simplejson.loads(gameevent)
        self.gameevent = gameevent
        
    def __repr__(self):
        '''
        String representation of the game event.
        
        :rtype: str
        '''
        return '<GameEvent. id: %s; session_id: %s; gameevent: %s [...]>' % (self.id, self.session_id, self.gameevent[:100])
    
    def __eq__(self, other):
        '''
        Checks if the gameevents are the same, if the sessionid is the same and the gameevent is exactly the same text.
        
        :param other:
        :rtype: boolean
        '''
        return self.id == other.id and self.gameevent == other.gameevent and self.session_id == other.session_id
    
    def as_dict(self):
        '''
        Returns dictionary version of game event. The gameevent itself, stored 
        in the database as serialized dictionary, is expanded in the dictionary as well. 
        
        :rtype: dict
        '''
        event_dict = simplejson.loads(self.gameevent)
        obj_d = {
            'id': self.id,
            'session_id': self.session_id,
            'gameevent': event_dict
        }
        return obj_d
        
    def as_hateoas(self):
        '''
        Returns dict representation of the game event that follows hateoas representation.
        
        :rtype: dict
        '''
       
        event_dict = simplejson.loads(self.gameevent)
       
        _links = []
        _self = {
            "rel" : "self",
            "href" : url_for("gameevents.get_event", sessionid= self.session_id, eventid=self.id)
        }
        _session = {
            "rel" : "session",
            "href" : url_for("gameevents.get_session", sessionid= self.session_id)
        }
        _links.append(_self)
        _links.append(_session)
        obj_d = {
            'id': self.id,
            'gameevent': event_dict,
            '_links':_links
        }
        return obj_d
    
    