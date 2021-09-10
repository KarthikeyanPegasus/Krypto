from time import sleep
import requests
from flask import Flask, jsonify, request, make_response
import jwt
import datetime
from functools import wraps
import threading


b = []

def apicall():
    main_api = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_d%20esc&per_page=100&page=1&sparkline=false"
    json_data = requests.get(main_api).json()
    bitcoin_info = json_data[0]
    bitcoin_price = bitcoin_info['current_price']
    return bitcoin_price

def checkprice(oldprice, target, currentprice):
    if oldprice < target:
        if target >= currentprice:
            return True
        else:
            return False
    else:
        if target <= currentprice:
            return True
        else:
            return False

def set_alert():
    currentprice = apicall()
    for i in b:
        target = i['target']
        if(checkprice(i['bitcoin_value'],target,currentprice)):
            print("trigger email")
            i['status']="triggered"
    
def infiniteloop():
    while True:
        set_alert()
        sleep(60)
            



app = Flask(__name__)

app.config['SECRET_KEY'] = 'thisisthesecretkey'

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return "missing, You can get the token from /login and after that use ?token=\"YOur token here\" at the end of the link"
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return "invalid, You can get the token from /login and after that use ?token=\"YOur token here\" at the end of the link"
        return f(*args,**kwargs)
    return decorator

@app.route('/alerts/create')
@token_required
def create():
    currentvalue = apicall()
    create_request = request.get_json(force=True)
    target = create_request['target']
    email = create_request['email']
    b.append({'target':target,'bitcoin_value':currentvalue,'status': "Not triggered",'email':email})
    return "Created"

@app.route('/alerts/delete')
@token_required
def delete():
    delete_request = request.get_json(force=True)
    target = delete_request['target']
    for k in b:
        if k['target'] == target:
            b.remove(k)
    return "deleted"

@app.route('/fetch')
@token_required
def fetch():
    ttl_page = 0
    c = len(b)
    while c>10:
        c = c-10
        ttl_page = ttl_page+1
    fetchs = jsonify({"No_of_pages":ttl_page,"instruction":"You can access by ../fetch/(Page_number)"})

    return fetchs



@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'Admin@123':
        token = jwt.encode({'user' : auth.username, 'exp':datetime.datetime.utcnow() + datetime.timedelta(minutes =30)},app.config['SECRET_KEY'])
        return jsonify({'token' : token})
        
    return make_response('Incorrect Username or Password!', 401, {'WWW-Authenticate':'Basic realm="Login Required"'})
if __name__ == '__main__':
   t1 = threading.Thread(target=app.run)
   t2 = threading.Thread(target=infiniteloop)
   t1.start()
   t2.start()
   t1.join()
   t1.join()
   


   
   