from flask import request
from random import randint

from app import app, mongo 

@app.route('/user/phone')
def user():

    # fetch request number
    num = request.args['num']

    # generate/store validation number
    validationNum = ''.join(['{}'.format(randint(0, 9)) for num in range(0, 6)])


    return validationNum
