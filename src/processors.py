import json
from flask import request, abort
from models import *
from flask_restless import ProcessingException
from openbts import check_node_manager_connection


def pos_error_test(result=None, **kw):
    test = [1, 2, 3]
    print test[7]


def pre_test(data=None, instance_id=None, search_params=None, **kw):
    print '\n\n\n'
    print 'Data:'
    print data
    print 'instance id:'
    print instance_id
    print 'parans:'
    print search_params
    print '\n\n\n'
    # pass


def make_error(status_code, sub_code, message, action):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message,
        'action': action
    })
    response.status_code = status_code
    return response


def auth(*args, **kargs):
    """
    Required API request to be authenticated
    """
    # if not current_user.is_authenticated():
    #    raise ProcessingException(description='Not authenticated', code=401)
    pass


def preprocessor_check_adm(*args, **kargs):
    # if not current_user.is_admin():
    #     raise ProcessingException(description='Forbidden', code=403)
    pass


def preprocessors_patch(instance_id=None, data=None, **kargs):
    user_cant_change = ["level", "clid", "_id",
                        "originated_calls", "received_calls"]
    admin_cant_change = ["_id", "originated_calls", "received_calls"]
    if current_user.is_admin():
        for x in data.keys():
            if x in admin_cant_change:
                raise ProcessingException(description='Forbidden', code=403)
    elif current_user.username == instance_id:
        for x in data.keys():
            if x in user_cant_change:
                raise ProcessingException(description='Forbidden', code=403)
    else:
        raise ProcessingException(description='Forbidden', code=403)


def preprocessors_check_adm_or_normal_user(instance_id=None, **kargs):
    if not (current_user.is_admin() or current_user.username == instance_id):
        raise ProcessingException(description='Forbidden', code=403)


def patch_user(instance_id=None, data=None, **kargs):
    # print data
    for i in range(len(data["fields"])):
        # it only works because we wont recive a bool
        if data["values"][i]:
            data[data["fields"][i]] = data["values"][i]
    del data["fields"]
    del data["values"]


def new_user(*args, **kargs):
    check_node_manager_connection()
    data = request.data
    request_body = json.loads(data)
    username = request_body['username']
    password = request_body['password']
    cpf = request_body['cpf']
    clid = request_body['clid']
    imsi = request_body['imsi']

    if username is None or password is None:
        abort(400)  # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(409)  # existing user
    if User.query.filter_by(cpf=cpf).first() is not None:
        abort(409)  # existing user
    if User.query.filter_by(clid=clid).first() is not None:
        abort(409)  # existing user
    if User.query.filter_by(imsi=imsi).first() is not None:
        abort(409)  # existing user
    # user = User(username = username)
    # user.hash_password(password)
    # db.session.add(user)
    # db.session.commit()
    # return jsonify({ 'username': user.username }), 201, {'Location':
    # url_for('get_user', id = user.id, _external = True)}


def new_scheduleuser(*args, **kargs):
    # check if the user is already in the group
    data = request.data
    request_body = json.loads(data)

    user_id = request_body['user_id']
    schedule_id = request_body['schedule_id']

    if ScheduleUser.query.filter_by(user_id=user_id, schedule_id=schedule_id).\
            first() is not None:
        abort(409)  # existing user

# Check if the user has a schedule


def schedule_exists(data=None, **kargs):
    data = request.data
    request_body = json.loads(data)
    schedule = Schedules.query.\
        filter_by(name=request_body['name']).first()
    if schedule is not None:
        raise ProcessingException(
            description='A schedule with this name already exists', code=400)
    else:
        pass


def voice_balance_postprocessor(result=None, **kw):
    for i in range(len(result['objects'])):
        if result['objects'][i]['to_user_id']:
            result['objects'][i]['to_user_clid'] = User.query.filter_by(
                _id=result['objects'][i]['to_user_id']).first().clid


def create_schedule_contract_post(search_params=None, **kw):
    pass


def create_schedule_contract_patch_single(search_params=None, **kw):
    pass


def create_schedule_contract_patch_many(data=None, search_params=None, **kw):
    print search_params
    print data
    # contract = ScheduleUser.query.filter(schedule_id= search_params[])
    for i in range(len(search_params['filters'])):
        if search_params['filters'][i]['name'] == 'schedule_id':
            schedule_id = search_params['filters'][i]['val']
        if search_params['filters'][i]['name'] == 'user_id':
            user_id = search_params['filters'][i]['val']

    schedule_user_id = ScheduleUser.query.filter_by(
        schedule_id=schedule_id, user_id=user_id).first()._id

    contract = ScheduleContract(
        schedule_user_id=schedule_user_id, months=data['number'])
    db.session.add(contract)
    db.session.commit()
    del data['number']


def inject_schedule_information(data=None, instance_id=None, search_params=None, result=None, **kw):
    print '\n\n\n'
    print 'Data:'
    print data
    print 'instance id:'
    print instance_id
    print 'parans:'
    print search_params
    print 'result:'
    print result
    print '\n\n\n'
    for i in range(result['num_results']):
        schedule = Schedules.query.filter_by(
            _id=result['objects'][i]['schedule_id']).first()
        result['objects'][i]['schedule_name'] = schedule.name
        result['objects'][i]['day'] = schedule.day
        result['objects'][i]['value'] = schedule.value
        result['objects'][i]['kind'] = schedule.kind
