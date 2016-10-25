import zmq
import json

def to_openbts(result=None, **kw):

    for key, value in result.items():
        if key == "_id":
            _id = value

        elif key == "clid":
            clid = value

        elif key == "imsi":
            imsi = value

    request =  {
                "command":"subscribers",
                "action":"create",
                "fields":{
                        "name": str(_id),
                        "imsi":"IMSI" + str(imsi),
                        "msisdn":str(clid) ,
                        "ki":""
                        }
                }


    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://127.0.0.1:45064")

    socket.send_string(json.dumps(request),encoding='utf-8')
