#!/usr/bin/env python

import datetime

import click
from flask.cli import with_appcontext

from app.db import write_to_db


@click.command("write-timestamp")
@with_appcontext
def write_timestamp():
    write_to_db(datetime.datetime.now())
