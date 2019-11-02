from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Load the default configuration
    app.config.from_object('config')

    # Load the configuration from the instance folder
    app.config.from_pyfile('config.py')

    login_manager.init_app(app)

    from .backend import backend as backend_blueprint
    app.register_blueprint(backend_blueprint, url_prefix='/backend')

    from .frontend import frontend as frontend_blueprint
    app.register_blueprint(frontend_blueprint, url_prefix='/')

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api/')

    return app
