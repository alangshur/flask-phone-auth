from flask import request
from random import randint
from datetime import datetime
import json, hashlib, secrets

from app import app, log, mongo, twilio, limiter
from app.util.token import authenticateBaseToken
from app.util.exception import CriticalException

@limiter.limit('1 per second')
@limiter.limit('1 per second', lambda: request.args['phone_number'])
@limiter.limit('1 per second', lambda: request.args['base_token'])
@app.route('/auth/phone')
def userPhone():
    internalSalt = 'PhoneAuth'
    try:

        # fetch request params
        phoneNumber = request.args['phone_number']

        # fetch header args
        baseToken = request.headers['base_token']

        # authenticate request
        if not authenticateBaseToken(baseToken, internalSalt, phoneNumber):
            raise CriticalException

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
        return json.dumps({ 
            'success': True
        })

    except CriticalException:
        log.error('Critical exception in /main/home')

        # send critical response
        return json.dumps({ 
            'success': False,
            'critical': True
        })

    except Exception as e:
        log.error('Exception in /main/home: ' + str(e))

        # send failure response
        return json.dumps({ 
            'success': False,
            'critical': False
        })

@limiter.limit('1 per second')
@limiter.limit('1 per second', lambda: request.args['validation_code'])
@limiter.limit('1 per second', lambda: request.args['base_token'])
@app.route('/auth/validate')
def userValidate():
    internalSalt = 'ValidateAuth'
    try:

        # fetch request params
        validationCode = request.args['validation_code']

        # fetch header args
        baseToken = request.headers['base_token']

        # authenticate request
        if not authenticateBaseToken(baseToken, internalSalt, validationCode):
            raise CriticalException

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
        return json.dumps({ 
            'success': True,
            'access_token': accessToken
        })

    except CriticalException:
        log.error('Critical exception in /main/home')

        # send critical response
        return json.dumps({ 
            'success': False,
            'critical': True
        })

    except Exception as e:
        log.error('Exception in /main/home: ' + str(e))

        # send failure response
        return json.dumps({ 
            'success': False,
            'critical': False
        })