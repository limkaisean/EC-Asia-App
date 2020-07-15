from flask import Flask, request
from flask_socketio import SocketIO

import time

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

# request.sid
class Socket:
    def __init__(self, sid):
        self.sid = sid
        self.connected = True

    # Emits data to a socket's unique room
    def emit(self, event, data):
        emit(event, data, room=self.sid)

orders = [
    {
        'id': 113,
        'time': '2:34 pm',
        'status': 'received',
        'drinks': []
    }, {
        'id': 112,
        'time': '2:32 pm',
        'status': 'preparing',
        'drinks': []
    }, {
        'id': 111,
        'time': '2:27 pm',
        'status': 'serving',
        'drinks': []
    }
]


customer_devices_orders = {

}

customer_devices_sockets = {

}

barista_devices_sockets = {

}

id = 0

@app.route("/")
def hello():
    print("Handling request to home page.")
    return "Hello Azure!"

@socketio.on('connect')
def test_connect():
    print('connected')
    socketio.emit('connect', {'data': 'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('update_order_status')
def message_handler(message):
    # update status in customer_devices_orders
    # send confirmation to barista devices
    # send status to barista devices
    # send status to customer device
    pass
    

@socketio.on('order_request')
def orders_handler(message):
    order = {}
    for drink in message.data:
        order[drink['id']] = drink['quantity']
    
    order['status'] = 'received'
    # add order to customer_devices_orders
    customer_devices_orders[id] = order
    id += 1

    # send confirmation and orders to customer device
    socketio.emit('order_response', {'isSuccesful': True, 'order': order})
    # send order to barista devices
    for bid in barista_devices_sockets:
        barista_devices_sockets[bid].emit('new_order', order)

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass

socketio.run(app)