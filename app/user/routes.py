from flask import request, Blueprint
from random import randint
from datetime import datetime
import json, time, hashlib, secrets

from app import app, mongo, client

@app.route('/user/phone')
def userPhone():
    try:

        # fetch request number (phone number)
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
    
    try:

        # fetch request number (validation code)
        num = request.args['num']

        # fetch validated user
        potUsers = mongo.db.pot_users.find({ 'validation_code': num })

        # verify correct code
        if potUsers.count() != 1: raise Exception
        for potUser in potUsers: phoneNumber = potUser['phone_number']

        # remove validated user
        mongo.db.pot_users.delete_one({ 'validation_code': num })

        # determine user ID
        hashFunc = hashlib.md5()
        saltedInput = (phoneNumber + app.config['USER_ID_SALT']).encode('utf-8')
        hashFunc.update(saltedInput)
        userID = hashFunc.hexdigest()       
        
        # generate user access token
        accessToken = secrets.token_hex(16)

        # store user profile
        user = mongo.db.users.find_one({ 'user_id': userID })
        if user:
            mongo.db.users.update_one({'user_id': userID }, {
                '$set': {
                    'user_id': userID,
                    'account_amount': user['account_amount'],
                    'access_token': accessToken
                }
            })
        else:
            mongo.db.users.insert_one({
                'user_id': userID,
                'account_amount': 0,
                'access_token': accessToken
            })
 
        # send success response
        response = { 
            'success': True,
            'access_token': accessToken
        }
        return json.dumps(response)

    except Exception as e:

        # log error
        app.logger.error(str(e))

        # send failure response
        response = { 'success': False }
        return json.dumps(response)