# sg-gameevents 
A module for service-based serious games that listen for game events coming from games.

## Requires

sudo apt-get install build-essential  build-dep libssl-dev libffi-dev python3-dev libxslt-dev libmysqlclient-dev python-mysqldb mysql-server

## Create an environment (Linux)

mkdir myproject

cd myproject

python3 -m venv venv

## Activate the environment (First, remember to activate the virtualenv, if any)

. venv/bin/activate

## Try it out

Install the requirements

pip install -r requirements.txt
 
Then, create the database and the migration files:

$ python gameevents/db_create.py
$ python gameevents/db_migrate.py

Run the server

$ python gameevents/run.py

Request an admin token:

$ curl -i -H "Content-Type: application/json" -X POST -d '{"clientid":"administrator","apikey":"YOURAPIKEY"}' http://localhost:5000/gameevents/api/v1.0/token

Add an admin client to the database using the admin token:

$ curl  -i -H "X-AUTH-TOKEN: YOURTOKEN" -H "Content-Type: application/json" -X POST -d '{"clientid":"CLIENTID", "apikey":"APIKEY", "role":"admin"}' http://localhost:5000/gameevents/api/v1.0/admin/clients

Add a normal client using the admin token

$ curl  -i -H "X-AUTH-TOKEN: YOURTOKEN" -H "Content-Type: application/json" -X POST -d '{"clientid":"CLIENTID", "apikey":"APIKEY"}' http://localhost:5000/gameevents/api/v1.0/admin/clients


Request a token (normal user):

$ curl -i -H "Content-Type: application/json" -X POST -d '{"clientid":"lix","apikey":"lixapikey"}' http://localhost:5000/gameevents/api/v1.0/token


Commit an event:
$ curl -i  -H "X-AUTH-TOKEN: YOURTOKEN" -H "Content-Type: application/json" -X POST -d '{"timestamp":"2015-11-10T20:30:00Z","gameevent":"<test></test>"}' http://localhost:5000/gameevents/api/v1.0/commitevent

See events commited in this session:
$ curl -i  -H "X-AUTH-TOKEN: YOURTOKEN" http://localhost:5000/gameevents/api/v1.0/sessions/SESSIONID/events

See existing sessions:
$ curl -i -H "Content-Type: application/json" -X POST -d '{"token":"YOURTOKEN"}' http://localhost:5000/gameevents/api/v1.0/sessions
