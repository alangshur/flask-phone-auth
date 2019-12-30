from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_pymongo import PyMongo
from flask.logging import create_logger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from twilio.rest import Client
import os

# launch flask app
app = Flask(__name__)

# configure logger
log = create_logger(app)

# configure correct environment
if os.environ.get('FLASK_ENV') == 'development': 
    app.config.from_object(DevelopmentConfig)
elif os.environ.get('FLASK_ENV') == 'production': 
    app.config.from_object(ProductionConfig)
else: log.error('Invalid Flask environment.')

# connect flask limiter
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['100 per second'],
)

# connect Twilio client
twilio = Client(app.config['TWILIO_SID'], app.config['TWILIO_AUTH_TOKEN'])

# connect mongo db
mongo = PyMongo(app)

from app.main import routes
from app.auth import routes