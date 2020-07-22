from flask import Flask, request
from flask_socketio import SocketIO

import time

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

# TODO: change request.sid to the meeting room number


STATUS_RECEIVED = 'received'
STATUS_PREPARING = 'preparing'
STATUS_SERVING = 'serving'
STATUS_COMPLETED = 'completed'

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
    print('Client connected')

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

@socketio.on('confirmed_orders_request')
def confirmed_orders_handler(message):
    order = {}

    # get socket
    # get orders for the socket
    if request.sid in customer_devices_orders:
        socketio.emit('confirmed_orders_response', customer_devices_orders[request.sid], room=request.sid)
    


@socketio.on('order_request')
def orders_handler(message):
    drinks = []
    for drinkId in message:
        drinks.append(message[drinkId])
    
    order = {}
    order['drinks'] = drinks
    order['status'] = STATUS_RECEIVED
    order['time'] = 2
    global id
    order['id'] = id
    id += 1

    # add order to customer_devices_orders
    if request.sid in customer_devices_orders:
        customer_devices_orders[request.sid].append(order)
    else:
        customer_devices_orders[request.sid] = [order]

    # send confirmation and orders to customer device
    socketio.emit('order_response', {'isSuccessful': True, 'order': order})
    # send order to barista devices
    for bid in barista_devices_sockets:
        barista_devices_sockets[bid].emit('new_order', order)

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass

socketio.run(app)
