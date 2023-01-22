# Budgeting Bob

This is a [Flask](https://flask.palletsprojects.com/en/1.1.x/) web application that is running on heroku.
It will store account transactions and categorize them for proper budgetting.

~There is a viewable demo with some [dummy data](https://github.com/ericmjalbert/budgeting-bob/blob/master/fill_demo_data.sh) to showcase the application: http://budgeting-bob-demo.herokuapp.com/. Login credentials for the demo are: `username = demo` and `password = demo`.~

EDIT: The above demo doesn't work anymore since heroku changed their stance on free-tier resources ([read more here](https://blog.heroku.com/next-chapter)).

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


## Data Import

### RBC CSV 

The current Upload Statements feature takes CSV's from RBC and uses those to populate all the fields for the transactions.

## Deployment

This service is currently setup to be deploy to Fly.io. 

Changes are build and deployed by merging to `master` branch.
Github actions handle all the steps needed to create the image and deploy it to all the fly.io environments (`demo` and `prd`).

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
