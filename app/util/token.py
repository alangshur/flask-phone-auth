import hashlib

from app import app

def authenticateBaseToken(token, internalSalt, number):

    # compute correct token
    hashFunc = hashlib.md5()
    saltedInput = (internalSalt + app.config['API_SALT'] + number).encode('utf-8')
    hashFunc.update(saltedInput)
    correctToken = hashFunc.hexdigest() 

    # return result 
    if correctToken != token: return False
    else: return True