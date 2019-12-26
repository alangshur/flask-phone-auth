from flask import Flask
from config import DevelopmentConfig, ProductionConfig
import os

# launch flask app
app = Flask(__name__)

# configure correct environment
if os.environ.get('FLASK_ENV') == 'development': 
    app.config.from_object(DevelopmentConfig)
elif os.environ.get('FLASK_ENV') == 'production': 
    app.config.from_object(ProductionConfig)
else: app.logger.error('Invalid Flask environment.')

from app import routes