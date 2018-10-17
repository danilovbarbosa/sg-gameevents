'''
Run the application
'''

# under normal circumstances, this script would not be necessary. the
# sample_application would have its own setup.py and be properly installed;
# however since it is not bundled in the sdist package, we need some hacks
# to make it work

import os
import sys

from gameevents_app.models.client import Client
from gameevents_app.models.gameevent import GameEvent
from gameevents_app.models.session import Session


sys.path.append(os.path.dirname(__name__))

#from sample_application import create_app
from gameevents_app import create_app

# create an app instance
if __name__ == "__main__":
    app = create_app()

    app.run(debug=True, port=5000, use_reloader=True)