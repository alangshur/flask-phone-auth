from app import app, mongo 

@app.route('/loot')
def loot():
    return "Loot API."
 