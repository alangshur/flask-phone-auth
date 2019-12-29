from flask import request, Blueprint
from random import randint
from datetime import datetime
import json, time, hashlib, secrets

from app import app, log, mongo, twilio
from app.util.token import authenticateBaseToken

@app.route('/user/phone')
def userPhone():
    internalSalt = 'PhoneAuth'
    try:

        # fetch request phone number
        baseToken = request.args['base_token']
        phoneNumber = request.args['phone_number']

        # authenticate request
        if not authenticateBaseToken(baseToken, internalSalt, phoneNumber): 
            raise Exception

        # generate/store validation number
        validationCode = ''.join(['{}'.format(randint(0, 9)) for phoneNumber in range(0, 6)])

        # document phone_number/validation_code
        mongo.db.pot_users.insert_one({
            'createdAt': datetime.utcnow(),
            'phone_number': phoneNumber,
            'validation_code': validationCode
        })

        # send validation message
        twilio.messages.create(
            messaging_service_sid=app.config['TWILIO_MESSAGING_SERVICE_SID'],
            to='+' + phoneNumber,
            body='Your Roam authentication number is ' + validationCode + '.'
        )

        # send success response
        response = { 'success': True }
        return json.dumps(response)

    except Exception as e:

        # log error
        log.error(str(e))

        # send failure response
        response = { 'success': False }
        return json.dumps(response)

@app.route('/user/validate')
def userValidate():
    internalSalt = 'ValidateAuth'
    try:
        
         # fetch request phone number
        baseToken = request.args['base_token']
        validationCode = request.args['validation_code']

        # authenticate request
        if not authenticateBaseToken(baseToken, internalSalt, validationCode): 
            raise Exception

        # fetch validated user
        potUsers = mongo.db.pot_users.find({ 'validation_code': validationCode })

        # verify correct code
        if potUsers.count() != 1: raise Exception
        for potUser in potUsers: phoneNumber = potUser['phone_number']

        # remove validated user
        mongo.db.pot_users.delete_one({ 'validation_code': validationCode })

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
                    'access_token': accessToken,
                    'account_amount': user['account_amount'],
                    'last_game_id': user['last_game_id']
                }
            })
        else:
            mongo.db.users.insert_one({
                'user_id': userID,
                'access_token': accessToken,
                'account_amount': 0,
                'last_game_id': None
            })
 
        # send success response
        response = { 
            'success': True,
            'access_token': accessToken
        }
        return json.dumps(response)

    except Exception as e:

        # log error
        log.error(str(e))

        # send failure response
        response = { 'success': False }
        return json.dumps(response)