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

Clone project (branch sg-eventsGameDeaf):

git clone -b sg-eventsGameDeaf https://github.com/danilovbarbosa/sg-gameevents.git

Install the requirements

pip install -r requirements.txt

Add file './gameevents/config.py' with configuration from: SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, WTF_CSRF_ENABLED, SECRET_KEY, SQLALCHEMY_DATABASE_URI_TEST, TMPDIR, LOG_FILENAME, LOG_FILENAME_TEST and DEFAULT_TOKEN_DURATION  
 
Then, create the database and the migration files:

** Remember, before you run the commands, you should create schemas in database MySql: gameevents and gameevents_test

$ python gameevents/db_create.py

$ python gameevents/db_migrate.py

Run the server

$ python gameevents/run.py

** Name user and apikey will print in screen so you save this informations

Request an admin token:

** You can change tags: clientid and apikey.

$ curl -i -H "Content-Type: application/json" -X POST -d '{"clientid":"administrator","apikey":"YOURAPIKEY"}' http://localhost:5000/v1/token

** When you run this command will be generated one token from admin (duration time: 600s), you can save for use in others operations. See examples operations below:

Add an admin client to the database using the admin token:

$ curl  -i -H "X-AUTH-TOKEN: YOURTOKEN" -H "Content-Type: application/json" -X POST -d '{"clientid":"CLIENTID", "apikey":"APIKEY", "role":"admin"}' http://localhost:5000/v1/clients

Add a normal client it's necessery one client with role: admin (tip: you can use same user and password of service userprofile for clientid and apikey, for this remember create user and session in service userprofile). 

$ curl  -i -H "X-AUTH-TOKEN: YOURTOKEN" -H "Content-Type: application/json" -X POST -d '{"clientid":"CLIENTID", "apikey":"APIKEY"}' http://localhost:5000/v1/clients


Request a token (normal user) it's necessery sessionid of :

$ curl -i -H "Content-Type: application/json" -X POST -d '{"clientid":"CLIENTID", "apikey":"APIKEY", "sessionid": "SESSIONID"}' http://localhost:5000/v1/token

See existing sessions:
$ curl -i -H "Content-Type: application/json" -X POST -d '{"token":"YOURTOKEN"}' http://localhost:5000/v1/sessions

Commit an event (Timestamps are recorded in the standardized format ISO 8601):

$ curl -i -H "X-AUTH-TOKEN: YOURTOKEN" -H "Content-Type: application/json" -X POST -d '{"timestamp":"DATA_DO_EVENTO: 2015-11-10T20:30:00Z","events":"{DICIONARIO_DE_EVENTOS}"}' http://localhost:5000/v1/sessions/SESSIONID/events

See events commited in this session:
$ curl -i  -H "X-AUTH-TOKEN: YOURTOKEN" http://localhost:5000/v1/sessions/SESSIONID/events


