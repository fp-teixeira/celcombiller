import zmq
import json
import socket as socket_pk
from config import NODE_MANAGER_ADDRESS, NODE_MANAGER_PORT
from flask import abort
from models import User


def check_node_manager_connection():
    # check if we have connection with nodemanager
    socket = socket_pk.socket(socket_pk.AF_INET, socket_pk.SOCK_STREAM)
    if socket.connect_ex((NODE_MANAGER_ADDRESS, int(NODE_MANAGER_PORT))):
        abort(500, "Conexao com o NodeManager Falhou")


def new_user_openbts(result=None, **kw):

    _id = str(result['_id'])
    clid = str(result['clid'])
    imsi = str(result['imsi'])

    request = {
        'command': 'subscribers',
        'action': 'create',
        'fields': {
            'name': _id,
            'imsi': 'IMSI' + imsi,
                    'msisdn': clid,
                    'ki': ''
        }
    }

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect('tcp://' + NODE_MANAGER_ADDRESS + ':' + NODE_MANAGER_PORT)
    socket.send_string(json.dumps(request), encoding='utf-8')

    # set timeout
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    if poller.poll(1000):  # 1s timeout in milliseconds
        msg = socket.recv_json()
    else:
        # TODO: what do we do when the request fail ?
        # raise IOError("Request to OpenBTS Timeout")
        socket.close(linger=1)
        context.term()
        abort(500, "Conexao com o NodeManager Falhou")

    socket.close(linger=1)
    context.term()


def patch_user_openbts(instance_id=None, data=None, **kw):
    """Fist I get the data to be modified then  delete the current information
    in the openbts database and finally I recreate the entrance in the OpenBTS
    database"""

    user = User.query.filter_by(username=instance_id).first()

    _id = str(user._id)
    if 'clid' not in data and  'imsi' not in data:
        return

    if 'clid' in data:
        clid = data['clid']
    else:
        clid = user.clid

    if 'imsi' in data:
        imsi_new = data['imsi']
        imsi_old = user.imsi
    else:
        imsi_new = user.imsi
        imsi_old = user.imsi

    delete_request = {
        'command': 'subscribers',
        'action': 'delete',
        'match': {
            'imsi': 'IMSI' + imsi_old,
        }
    }

    create_request = {
        'command': 'subscribers',
        'action': 'create',
        'fields': {
            'name': _id,
            'imsi': 'IMSI' + imsi_new,
                    'msisdn': clid,
                    'ki': ''
        }
    }

    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://" + NODE_MANAGER_ADDRESS + ':' + NODE_MANAGER_PORT)
    socket.send_string(json.dumps(delete_request), encoding='utf-8')
    # socket.send_string(json.dumps(create_request), encoding='utf-8')
    # set timeout to send
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    if poller.poll(1000):  # 1s timeout in milliseconds
        msg = socket.recv_json()
    else:
        # TODO: what do we do when the request fail ?
        # raise IOError("Request to OpenBTS Timeout")
        socket.close(linger=1)
        context.term()
        abort(500, "Conexao com o NodeManager Falhou")


    socket.send_string(json.dumps(create_request), encoding='utf-8')
    poller = zmq.Poller()
    poller.register(socket, zmq.POLLIN)
    if poller.poll(1000):  # 1s timeout in milliseconds
        msg = socket.recv_json()
    else:
        # TODO: what do we do when the request fail ?
        # raise IOError("Request to OpenBTS Timeout")
        socket.close(linger=1)
        context.term()
        abort(500, "Conexao com o NodeManager Falhou")


    socket.close(linger=1)
    context.term()
