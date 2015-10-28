'''
Creates a few custom exceptions used throughout the application.
'''

class SessionNotActive(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
    
class TokenExpired(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)