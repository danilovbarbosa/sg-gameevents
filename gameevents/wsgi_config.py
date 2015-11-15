import sys

path = '/home/carvalhomb/sg-dashboard/dashboard'
if path not in sys.path:
    sys.path.append(path)

from dashboard_app import create_app

application = create_app()