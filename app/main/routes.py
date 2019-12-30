from flask import request
from flask_limiter import Limiter
import json, time

from app import app, log, mongo, twilio, limiter
from app.util.token import authenticateBaseToken
from app.util.exception import CriticalException, RefreshException

@limiter.limit('1 per second')
@limiter.limit('1 per second', lambda: request.headers['base_token'])
@limiter.limit('1 per second', lambda: request.headers['access_token'])
@app.route('/main/home')
def home():
    internalSalt = 'HomeMain'
    try: 

        # fetch request params
        artificialTarget = request.args['artificial_target']

        # fetch header args
        baseToken = request.headers['base_token']
        accessToken = request.headers['access_token']

        # authenticate request (base token)
        if not authenticateBaseToken(baseToken, internalSalt, artificialTarget):
            raise CriticalException

        # authenticate request (access token)
        users = mongo.db.users.find({ 'access_token': accessToken })
        if users.count() != 1: raise RefreshException

        ## USE FLASK CACHE TO CACHE RECENT ACCESS TOKENS (WITH TIMEOUT)

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
        log.error('Exception in /main/home: ' + str(e))

        # send failure response
        return json.dumps({ 
            'success': False,
            'critical': False,
            'refresh': False
        }) 