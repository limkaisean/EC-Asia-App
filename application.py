from flask import Flask, request
from flask_socketio import SocketIO

import pytz
from datetime import datetime

tz = pytz.timezone("Asia/Singapore")

app = Flask(__name__)
socketio = SocketIO(app)
socketio.init_app(app, cors_allowed_origins="*")

# ASSUMPTION: there can only be one session per meeting room
# TODO: update meeting room socket on connecting

STATUS_RECEIVED = 'received'
STATUS_PREPARING = 'preparing'
STATUS_SERVING = 'serving'
STATUS_COMPLETED = 'completed'

customer_devices_sockets = {}
customer_devices_orders = {}
barista_devices = []
id = 0

@app.route("/")
def hello():
    print("Handling request to home page.")
    return "Hello Azure!"

@socketio.on('connect')
def connect():
    print('Client connected')
    socketio.emit('connected', {})

@socketio.on('disconnect')
def disconnect():
    if request.sid in barista_devices:
        barista_devices.remove(request.sid)

@socketio.on('connect_info')
def connect_info(message):
    print('connect_info')
    customer_devices_sockets[meeting_room] = request.sid

@socketio.on('update_status_request')
def message_handler(message):
    try:
        if request.sid not in barista_devices:
            barista_devices.append(request.sid)
        
        oId = message['id']
        meeting_room = str(message['meetingRoom'])
        status = message['status']

        if status == STATUS_COMPLETED:
            customer_devices_orders[meeting_room].pop(oId)
        else:
            customer_devices_orders[meeting_room][oId]['status'] = status

        for b in barista_devices:
            socketio.emit('update_orders', { 'isSuccessful': True, 'orders': customer_devices_orders[meeting_room]}, room=b)

        socketio.emit('update_status_relay', message, room=customer_devices_sockets[meeting_room])
    except Exception as e:
        print('Error2:', e)

@socketio.on('barista_orders_request')
def barista_orders(message):
    try:
        if request.sid not in barista_devices:
            barista_devices.append(request.sid) 
        
        all_orders = customer_devices_orders.values()
        all_orders_flat = {oId: room_orders[oId] for room_orders in all_orders for oId in room_orders}
        socketio.emit('barista_orders_response', all_orders_flat)
    except Exception as e:
        print('Error bar', e)

@socketio.on('confirmed_orders_request')
def confirmed_orders(message):
    try:
        meeting_room = str(message['meetingRoom'])
        customer_devices_sockets[meeting_room] = request.sid
        socketio.emit('confirmed_orders_response', customer_devices_orders[meeting_room])
    except Exception as e:
        print('Error orders req', e)

@socketio.on('order_request')
def order(message):
    try:        
        order = {}
        order['beverages'] = message['beverages']
        order['status'] = STATUS_RECEIVED

        # get Singapore time in 'hh:mm period' format
        order['time'] = tz.localize(datetime.now(), is_dst=None).strftime('%l:%M %p')
        global id
        order['id'] = id
        id += 1
        
        meeting_room = str(message['meetingRoom'])
        order['meetingRoom'] = meeting_room

        # add order to customer_devices_orders
        if meeting_room in customer_devices_orders:
            customer_devices_orders[meeting_room][order['id']] = order
        else:
            customer_devices_orders[meeting_room] = { order['id']: order }

        customer_devices_sockets[meeting_room] = request.sid

        # send confirmation and orders to customer device
        socketio.emit('order_response', {'isSuccessful': True, 'order': order})
        # send order to barista devices

        all_orders = customer_devices_orders.values()
        all_orders_flat = {oId: room_orders[oId] for room_orders in all_orders for oId in room_orders}
        for bid in barista_devices:
            socketio.emit('barista_orders_response', all_orders_flat, room=bid)
    except Exception as e:
        print('Error:', e)

@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    pass

socketio.run(app)
