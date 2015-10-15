'''
Created on 15 Oct 2015

@author: mbrandaoca
'''

class SessionNotActive(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)