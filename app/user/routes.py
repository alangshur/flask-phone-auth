from app import app, mongo 

@app.route('/user')
def user():
    return "User API."
