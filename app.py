from flask import Flask
from flask.logging import create_logger
import os

# configure app
app = Flask(__name__)
log = create_logger(app)
app.config.from_object(os.environ['APP_SETTINGS'])

@app.route('/')
def hello():
    return "Hello World!"

# run app
if __name__ == '__main__':
    app.run()