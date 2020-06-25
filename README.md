# Budgeting Bob

This is a [Flask](https://flask.palletsprojects.com/en/1.1.x/) web application that is running on heroku.
It will store account transactions and categorize them for proper budgetting.

There is a viewable demo with some [dummy data](https://github.com/ericmjalbert/budgeting-bob/blob/master/fill_demo_data.sh) to showcase the application: http://budgeting-bob-demo.herokuapp.com/. Login credentials for the demo are: `username = demo` and `password = demo`.

## Installation

Create a virtualenv named `venv` and then `pip install -r requirements.txt`.

## Usage

To run the webapp locally:
```bash
FLASK_DEBUG=1 FLASK_APP=app venv/bin/python -m flask run
```

## User Access

To avoid having multiple users using a single instance of this (that's not a feature I wanted to build out) I limited the login and registration to only work for 2 usernames.
This way I have public access to my own instance and its password protected to avoid others from accessing it.

The second username is made available for the demo usage.


## Database Initilization

This whole thing is running on Heroku cloud platform so local dev connects directly to the heroku database.
To complete this just have a `.env` (use `.env.template` as example) with the Database URL from heroku (use `heroku pg:credentials:url --app budgeting-bob-demo | grep postgres` to get the URL).

Once you got a database, you can initialize all the table by running the `./initialize_db_demo.sh` script. Feel free to edit it as this data was setup for demo purposes.


## RBC CSV automation

There exist's a Selenium script that will log into RBC and navigate to the "Download CSV" button and then load it into the database.
To run this I use:
```bash
FLASK_DEBUG=1 FLASK_APP=app venv/bin/python -m flask import-rbc-csv ERIC
```

There are a list of secrets in the .env.template that correspond to this automation script.
Understand that this whole feature is very experimental and it fails sometimes.
The [source code](https://github.com/ericmjalbert/budgeting-bob/blob/master/app/scripts/selenium_import_rbc_csv.py) can be edited to match your specific needs.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
