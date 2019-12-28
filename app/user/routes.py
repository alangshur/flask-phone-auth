from flask import request
from random import randint
from datetime import datetime
import json

from app import app, mongo, client

@app.route('/user/phone')
def userPhone():
    try:

        # fetch request number
        num = request.args['num']

        # generate/store validation number
        validationCode = ''.join(['{}'.format(randint(0, 9)) for num in range(0, 6)])

        # document num/validation_code
        mongo.db.pot_users.insert_one({
            'createdAt': datetime.utcnow(),
            'phone_number': num,
            'validation_code': validationCode
        })

        # send validation message
        client.messages.create(
            messaging_service_sid=app.config['TWILIO_MESSAGING_SERVICE_SID'],
            to='+' + num,
            body='Your Roam authentication number is ' + validationCode + '.'
        )

        # send success response
        response = { 'success': True }
        return json.dumps(response)

    except Exception as e:

        # log error
        app.logger.error(str(e))

        # send failure response
        response = { 'success': False }
        return json.dumps(response)

@app.route('/user/validate')
def userValidate():
    pass