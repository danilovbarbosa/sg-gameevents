'''
Created on 14 Oct 2015

@author: mbrandaoca
'''

from sqlalchemy import *
from base import Base
from sqlalchemy.orm import relationship

########################################################################
class GamingSession(Base):
    """"""
    __tablename__ = "gamingsession"
 
    id = Column(Integer, primary_key=True)
    status = Column(Boolean)
 
    #----------------------------------------------------------------------
    def __init__(self):
        """"""
        #self.id = name
        self.status = 1