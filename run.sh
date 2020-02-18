bash ./initialize_db.sh "heroku pg:psql"
FLASK_DEBUG=1 FLASK_APP=app venv/bin/python -m flask run
