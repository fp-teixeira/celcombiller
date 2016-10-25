# -*- coding: utf-8 -*-
from flask import request, flash, render_template, jsonify
from flask.ext.restless import APIManager
from setup import db, app, login_manager
from models import *
from datetime import datetime
from flask_restless import ProcessingException
from flask.ext.login import login_user, logout_user, current_user,\
    login_required
import json
from openbts import new_user_openbts, patch_user_openbts
from processors import *

# to return the errors


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/test', methods=['GET'])
@login_required
def test():
    # print 'ok'
    # print json.loads({"roles": ["user"],
    #                  "displayName": "test test",
    #                  "username": "test"})
    # return json.loads({"roles":["user"],"displayName":"test
    # test","username":"test"})
    return "test"


@app.route('/', methods=['GET', 'POST'])
def index():
    """
    Index page, just show the logged username
    """
    try:
        if current_user.is_authenticated():
            return render_template('index.html')
        else:
            return "no else"
    except Exception:
        return render_template('anonymous.html')


# Login, if the user does not exist it returs a error page
@app.route('/login', methods=['POST'])
def login():

    # if request.method == 'GET':
    #     return render_template('login.html')
    # else:
    #     username = request.form['username']
    #     password = request.form['password']
    #     registered_user = \
    #         User.query.filter_by(username=username, password=password).first()
    #     if registered_user is None:
    #         flash('Username or Password is invalid', 'error')
    #         return render_template('ERROR.html')
    #     if login_user(registered_user):
    #         return "Hello, cross-origin-world! " + current_user.name
    #     else:
    #         flash('Flask Login error', 'error')
    #         return render_template('ERROR.html')

    level = ["admin", "user", "coll"]
    data = json.loads(request.data)
    user = User.query.filter_by(
        username=data['username'], password=data["password"]).first()
    if user:
        login_user(user)
        return json.dumps({"roles": [level[user.level]],
                           "displayName": user.name,
                           "username": user.username,
                           "id": user._id
                           })
    else:
        raise InvalidUsage(u'Usuário ou Senha invalido', status_code=404)


@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None


@login_manager.request_loader
def load_user_from_request(request):

    # first, try to login using the api_key url arg
    api_key = request.args.get('api_key')
    if api_key:
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # next, try to login using Basic Auth
    api_key = request.headers.get('Authorization')
    if api_key:
        api_key = api_key.replace('Basic ', '', 1)
        try:
            api_key = base64.b64decode(api_key)
        except TypeError:
            pass
        user = User.query.filter_by(api_key=api_key).first()
        if user:
            return user

    # finally, return None if both methods did not login the user
    return None

# Returns the user data balance


@app.route('/check_data_balance', methods=['GET', 'POST'])
def check_data_balance(*args, **kargs):
    data = request.data
    request_body = json.loads(data)
    # Is it a better way to handle the exception when the user is not found ?
    try:
        x = User.query.filter_by(
            imsi=request_body['imsi']).first().DataBalance()
        return str(x)
    except AttributeError:
        return "none"

# Returns the user voice balance


@app.route('/check_voice_balance', methods=['GET', 'POST'])
def check_voice_balance(*args, **kargs):
    data = request.data
    request_body = json.loads(data)
    # Is it a better way to handle the exception when the user is not found ?
    try:
        x = User.query.filter_by(
            imsi=request_body['imsi']).first().VoiceBalance()
        return str(x)
    except AttributeError:
        return "none"


# I dont know what this function does so I commented it.
# def check_time():
#     if not current_user.is_admin():
#         return False
#     else:
#         json_need_update = []
#         schedules = Schedules.query.all()
#         for schedule in schedules:
#             boolean_time = (schedule.dates_to_update[0].date - datetime.now())\
#                 .total_seconds()
#             boolean_time = 1 if boolean_time < 0 else 0
#             if boolean_time == 1:
#                 json_need_update.append(schedule.name)
#         if json_need_update == []:
#             return None
#         else:
#             return json_need_update


# Let's put onlt one user at time in the schedule
# def put_user__idin_buffer(*args, **kargs):
#     data = request.data
#     request_body = json.loads(data)
#     global buffer_users_id
#     buffer_users_id = request_body['users']
#     del kargs['data']['users']

# def add_users_to_schedule(*args, **kargs):
#     global buffer_users_id
#     data = request.data
#     request_body = json.loads(data)
#     schedule = Schedules.query\
#         .filter_by(name=request_body['name']).first()
#     #for user_id in buffer_users_id:
#     user = User.query.filter_by(_id=user_id).first()
#         schedule.tunel.append(user)
#     db.session.add(schedule)
#     db.session.commit()
#     pass

# def add_dates_to_schedule(*args, **kargs):
#     global data_count
#     data = request.data
#     request_body = json.loads(data)
#     schedule = Schedules.query.\
#         filter_by(name=request_body['name']).first()
#     listOfdates = Dates.query.order_by(Dates._id.desc()).limit(data_count)
#     for date in listOfdates:
#         schedule.dates_to_update.append(date)
#     pass


def transform_to_utc(*args, **kargs):
    global data_count
    data = request.data
    request_body = json.loads(data)
    data_count = kargs['data']['count']
    min_day = int(datetime.now().strftime("%d"))
    min_month = int(datetime.now().strftime("%m"))
    min_year = int(datetime.now().strftime("%Y"))
    day = int(request_body['day'])
    year = int(request_body['year'])
    month = int(request_body['month'])
    how_many = int(request_body['count'])
    if year < min_year or ((month < min_month) and (year <= min_year)) or \
            (day < min_day and (month <= min_month and year <= min_year)):
        raise ProcessingException(description='Date not accept', code=400)
    else:
        del kargs['data']['day']
        del kargs['data']['month']
        del kargs['data']['year']
        del kargs['data']['count']
        start_date = str(month) + " " + str(day) + " " + str(year) + " 0:0:0 "
        all_dates = \
            list(rrule(MONTHLY, count=how_many, dtstart=parse(start_date)))
        for var in all_dates:
            db.session.add(Dates(var))
            db.session.commit()
        pass

# def date_now(*args, **kargs):
#     kargs['data']['date'] = unicode(datetime.now())
#     global buffer_users_id
#     buffer_users_id = kargs['data']['user_id']
#     #del kargs['data']['user_id']


def add_user_data_balance(*args, **kargs):
    global buffer_users_id
    data = request.data
    request_body = json.loads(data)
    # Check if we are passing the user id or the imsi in the user_id field, it
    # is necessary because Openbts users IMSI only.
    if request_body['user_id'] < 1e13:
        x = DataBalance.query.order_by(DataBalance._id.desc()).first()
        x.users_id = request_body['user_id']
    else:
        x = DataBalance.query.order_by(Balance._id.desc()).first()
        x.users_id = User.query.filter_by(
            imsi=request_body['user_id']).first()._id
    db.session.add(x)
    db.session.commit()


def add_user_voice_balance(*args, **kargs):
    global buffer_users_id
    data = request.data
    request_body = json.loads(data)

    x = VoiceBalance.query.order_by(VoiceBalance._id.desc()).first()
    x.users_id = request_body['from_user_id']

    db.session.add(x)
    db.session.commit()


@app.route('/logout')
def logout():
    logout_user()
    return render_template('logout.html')


@login_manager.user_loader
def load_user(_id):
    return User.query.get(int(_id))


@app.route('/check')
@login_required
def check_login():
    """
    Index page, just show the logged username
    """
    return render_template('check.html')


@app.route('/checkadm')
def checkadm():
    """
    Index page, just show the logged username
    """

    return str(current_user)


manager = APIManager(app, flask_sqlalchemy_db=db)

# Create the Flask-Restless API manager.
# Create API endpoints, which will be available at /api/<tablename> by
# default. Allowed HTTP methods can be specified as well.

manager.create_api(
    User,
    preprocessors={
        'POST': [
            # auth,
            # preprocessor_check_adm
            new_user
        ],
        'GET_MANY': [
            # auth,
            # preprocessor_check_adm
        ],
        'GET_SINGLE': [
            # auth,
            # preprocessors_check_adm_or_normal_user
        ],
        'PATCH_SINGLE': [
            patch_user,
            patch_user_openbts
            # auth,
            # preprocessors_check_adm_or_normal_user,
            # preprocessors_patch
        ],
        'PATCH_MANY': [
            # auth, preprocessor_check_adm
            # auth,
        ],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        'POST': [
            new_user_openbts
        ],
        'PATCH_SINGLE': [
        ],
    },
    exclude_columns=[
        'password'
    ],
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    allow_patch_many=True,
    primary_key='username'
)

manager.create_api(
    Schedules,
    preprocessors={
        'POST': [
            # auth,
            # preprocessor_check_adm,
            # schedule_exists,
            # put_user__idin_buffer,
            # transform_to_utc
        ],
        'GET_MANY': [
            auth,
            preprocessor_check_adm
        ],
        'GET_SINGLE': [auth, preprocessor_check_adm],
        'PATCH_SINGLE': [
            auth,
            preprocessor_check_adm
        ],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        # 'POST': [add_dates_to_schedule, add_users_to_schedule],
        'POST': [],
    },
    exclude_columns=[
        'newUser',
        'removeUser',
        'updateSchedule'
    ],
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    results_per_page=100
)

manager.create_api(
    ScheduleUser,
    preprocessors={
        'POST': [
            preprocessor_check_adm,
            new_scheduleuser,
            create_schedule_contract_post
            # pre_test
        ],
        'GET_MANY': [
            auth,
            preprocessor_check_adm
        ],
        'GET_SINGLE': [auth, preprocessor_check_adm],
        'PATCH_SINGLE': [
            auth,
            preprocessor_check_adm,
            create_schedule_contract_patch_single,
            # pre_test
        ],
        'PATCH_MANY': [
            auth,
            preprocessor_check_adm,
            create_schedule_contract_patch_many,
            # pre_test
        ],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        'GET_MANY': [
            inject_schedule_information
        ]
    },
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    results_per_page=100,
    allow_patch_many=True
)


manager.create_api(
    ScheduleContract,
    preprocessors={
        'GET_MANY': [
            auth,
            preprocessor_check_adm
        ],
        'GET_SINGLE': [
            auth, preprocessor_check_adm
        ],
    },
    postprocessors={
    },
    methods=['GET'],
    results_per_page=100,
    allow_patch_many=True
)


manager.create_api(
    VoiceBalance,
    preprocessors={
        'POST': [
            # preprocessor_check_adm,
            # date_now
        ],
        'GET_MANY': [
            auth,
            preprocessor_check_adm,
            pre_test
        ],
        'GET_SINGLE': [auth, preprocessor_check_adm],
        'PATCH_SINGLE': [
            auth,
            preprocessor_check_adm
        ],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        'POST': [add_user_voice_balance],
        'GET_MANY': [voice_balance_postprocessor]
    },
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    results_per_page=100,
)

manager.create_api(
    DataBalance,
    preprocessors={
        'POST': [
            #           preprocessor_check_adm,
            # date_now
        ],
        'GET_MANY': [
            auth,
            preprocessor_check_adm
        ],
        'GET_SINGLE': [auth, preprocessor_check_adm],
        'PATCH_SINGLE': [
            auth,
            preprocessor_check_adm
        ],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        'POST': [add_user_data_balance]
    },
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    results_per_page=100,
)


manager.create_api(
    ScheduleInput,
    preprocessors={
        'POST': [
            preprocessor_check_adm,
            # date_now
        ],
        'GET_MANY': [
            auth,
            preprocessor_check_adm
        ],
        'GET_SINGLE': [auth, preprocessor_check_adm],
        'PATCH_SINGLE': [
            auth,
            preprocessor_check_adm
        ],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        'POST': []
    },
    methods=['POST', 'GET', 'PATCH', 'DELETE'],
    results_per_page=100,
)
