from flask import request
import json, time

from app import app, log, mongo, twilio
from app.util.token import authenticateBaseToken
from app.util.exception import CriticalException, RefreshException

@app.route('/main/home')
def home():
    internalSalt = 'HomeMain'
    try: 

        # authenticate request (base token)
        baseToken = request.args['base_token']
        artificialTarget = request.args['artificial_target']
        if not authenticateBaseToken(baseToken, internalSalt, artificialTarget):
            raise CriticalException

        # authenticate request (access token)
        accessToken = request.args['access_token']
        users = mongo.db.users.find({ 'access_token': accessToken })
        if users.count() != 1: raise RefreshException

        # send success response
        return json.dumps({ 
            'success': True,
            'payload': 'Successful double authentication!'
        })

    except CriticalException:
        log.error('Critical exception in /main/home')

        # send critical response
        return json.dumps({ 
            'success': False,
            'critical': True,
            'refresh': False
        })

    except RefreshException:
        log.error('Refresh exception in /main/home')
        
        # send refresh response
        return json.dumps({ 
            'success': False,
            'critical': False,
            'refresh': True
        })

    except Exception as e:
        log.error('Exception in /main/home')

        # send failure response
        return json.dumps({ 
            'success': False,
            'critical': False,
            'refresh': False
        }) 