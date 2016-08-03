import flask
from flask import request, flash, render_template
from config import db, app, login_manager
from models import User, VoiceBalance, DataBalance, Schedules, ScheduleInput, \
    ScheduleUser
from datetime import *
from dateutil.rrule import *
from dateutil.parser import *
from dateutil.relativedelta import *
from flask_restless import ProcessingException
from flask.ext.login import login_user, logout_user, current_user,\
    login_required
import json
from openbts import to_openbts


@app.route('/')
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

@app.route('/test',methods=['GET'])
def test():
    return "rodou"

# Login, if the user does not exist it returs a error page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']
        registered_user = \
            User.query.filter_by(username=username, password=password).first()
        if registered_user is None:
            flash('Username or Password is invalid', 'error')
            return render_template('ERROR.html')
        if login_user(registered_user):
            return "Hello, cross-origin-world!"
        else:
            flash('Flask Login error', 'error')
            return render_template('ERROR.html')
        # json_with_names = check_time()


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


def auth(*args, **kargs):
    """
    Required API request to be authenticated
    """
    #if not current_user.is_authenticated():
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

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

# Create the Flask-Restless API manager.
# Create API endpoints, which will be available at /pi/<tablename> by
# default. Allowed HTTP methods can be specified as well.

manager.create_api(
    User,
    preprocessors={
        'POST': [
            # auth,
            # preprocessor_check_adm
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
            auth,
            preprocessors_check_adm_or_normal_user,
            preprocessors_patch
        ],
        'PATCH_MANY': [auth, preprocessor_check_adm],
        'DELETE_SINGLE': [auth, preprocessor_check_adm],
    },
    postprocessors={
        'POST': [to_openbts]
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
            transform_to_utc
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


manager.create_api(
    VoiceBalance,
    preprocessors={
        'POST': [
           #preprocessor_check_adm,
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
        'POST': [add_user_voice_balance]
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


# start the flask loop
app.debug = True
app.run('0.0.0.0', 5000)
