import sqlite3

import click
from flask import current_app, g 
# g is special object used to store data 
# accessed by multiple functions


# getter function for db connect
def get_db():
    # check if db is not loaded in flask
    if 'db' not in g:
        # connect to db named DATABASE and parse data types
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )

        # returns rows like dicts, helps to access columns by name
        g.db.row_factory = sqlite3.Row

        return g.db

# every connection needs to be closed
def close_db(e=None):
    # pop db from flask memory
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

#click.command defines command line command called init-db 
# which calls init_db function and shows a success message
@click.command('init-db')
def init_db_command():
    # clear the existing data and create new tables
    init_db()
    click.echo('Initialize the database')
    
# the functions close_db and init_db_command need to be registered with 
# the application instance. To make those instances available write init_app
# also import and call this function by placing at end of the factory before returning app
def init_app(app):
    #clean up after returning the resource
    app.teardown_appcontext(close_db)
    # this adds cli command with flask command
    app.cli.add_command(init_db_command)
