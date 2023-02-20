import os

from flask import Flask

def create_app(test_config=None):
    #create and configure the app
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY = 'dev',
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    if test_config is None:
        #when tests not run load the instance config
        app.config.from_pyfile('config.py',silent=True)
    else:
        # else load the test config file
        app.config.from_mapping(test_config)
    
    # this makes sure the instance folder exists 
    # SQL database file is present here
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # below route is a decorator that binds url
    # hello to function hello
    @app.route('/hello')
    def hello():
        return 'Hello World!'
    
    from . import db
    db.init_app(app)

    # import and register the blueprint from factory
    from . import auth
    app.register_blueprint(auth.bp)

    return app 
