# Budgeting Bob

This is a heroku web application that will store account transactions and categorize them for proper budgetting.

## Installation

Create a virtualenv named `venv` and then `pip install -r requirements.txt`. 

## Usage

To run the webapp locally:
```bash
FLASK_DEBUG=1 FLASK_APP=app venv/bin/python -m flask run
```

To run the CSV import file:
```bash
FLASK_DEBUG=1 FLASK_APP=app venv/bin/python -m flask import-rbc-csv OWNER_NAME
```

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)
