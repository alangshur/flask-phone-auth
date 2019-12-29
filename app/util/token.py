import hashlib

from app import app

def authenticateBaseToken(token, internalSalt, target):

    # compute correct token
    hashFunc = hashlib.md5()
    saltedInput = (internalSalt + app.config['API_SALT'] + target).encode('utf-8')
    hashFunc.update(saltedInput)
    correctToken = hashFunc.hexdigest() 

    # return result 
    return correctToken == token