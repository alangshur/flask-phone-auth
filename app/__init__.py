from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from flask_pymongo import PyMongo
import os

# launch flask app
app = Flask(__name__)

# configure correct environment
if os.environ.get('FLASK_ENV') == 'development': 
    app.config.from_object(DevelopmentConfig)
elif os.environ.get('FLASK_ENV') == 'production': 
    app.config.from_object(ProductionConfig)
else: app.logger.error('Invalid Flask environment.')

# connect mongo db
mongo = PyMongo(app)

from app.loot import routes
from app.user import routes