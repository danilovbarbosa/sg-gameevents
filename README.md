# sg-assess-adapt
An assessment and adaptation module for service-based serious games

## Requires

sudo apt-get install build-essential libssl-dev libffi-dev python3-dev


pip install flask flask-sqlalchemy flask-auth flask-api pyOpenSSL cryptography passlib sqlalchemy-migrate

## Try it out

First, remember to activate the virtualenv, if any
 
Then, create the database and the migration files:

$ python gameevents/db_create.py
$ python gameevents/db_migrate.py

Run the server

$ python gameevents/run.py

Add a client to the database:

$ curl -i -H "Content-Type: application/json" -X POST -d '{"clientid":"myclientid","apikey":"myapikey"}' http://localhost:5000/gameevents/api/v1.0/client

Request a token:

$ curl -i -H "Content-Type: application/json" -X POST -d '{"clientid":"myclientid","apikey":"myapikey"}' http://localhost:5000/gameevents/api/v1.0/token

