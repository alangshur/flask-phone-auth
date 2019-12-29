from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_pymongo import PyMongo
from flask.logging import create_logger
from twilio.rest import Client
import os

# launch flask app
app = Flask(__name__)
log = create_logger(app)

# configure correct environment
if os.environ.get('FLASK_ENV') == 'development': 
    app.config.from_object(DevelopmentConfig)
elif os.environ.get('FLASK_ENV') == 'production': 
    app.config.from_object(ProductionConfig)
else: log.error('Invalid Flask environment.')

# connect Twilio client
twilio = Client(app.config['TWILIO_SID'], app.config['TWILIO_AUTH_TOKEN'])

# connect mongo db
mongo = PyMongo(app)

from app.loot import routes
from app.user import routes