import sys, os
INTERP = os.path.join(os.environ['HOME'], '.virtualenvs', 'env', 'bin', 'python')
print(INTERP)
if sys.executable != INTERP:
	os.execl(INTERP, INTERP, *sys.argv)

current_dir = os.getcwd()
app_dir = os.path.join(current_dir, 'dashboard')
#sys.path.append(os.getcwd())
sys.path.append(app_dir)


from dashboard_app import create_app

application = create_app()



# Uncomment next two lines to enable debugging
#from werkzeug.debug import DebuggedApplication
#application = DebuggedApplication(application, evalex=True)

#from flask import Flask
#application = Flask(__name__)

#@application.route('/')
#def index():
#	return 'Hello passenger'
