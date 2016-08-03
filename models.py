from config import db, app
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm.session import object_session
from sqlalchemy.dialects.postgresql import ENUM
from datetime import *

row2dict = lambda r: {c.name: str(getattr(r, c.name))
                      for c in r.__table__.columns}

# Create your Flask-SQLALchemy models as usual but with the following two
# (reasonable) restrictions:
#   1. They must have a primary key column of type sqlalchemy.Integer or
#      type sqlalchemy.Unicode.
#   2. They must have an __init__ method which accepts keyword arguments for
#      all columns (the constructor in flask.ext.sqlalchemy.SQLAlchemy.Model
#      supplies such a method, so you don't need to declare a new one).


class User(db.Model):
    """
    System users each of which has a unique caller id (CLID)
    """
    __tablename__ = 'users'

    _id = db.Column(db.Integer, primary_key=True, nullable=False)
    level = db.Column(db.Integer, nullable=False) # 0=administrator, 1=users, 2=collaborator
    name = db.Column(db.Unicode, nullable=False)
    address = db.Column(db.Unicode)
    cpf = db.Column(db.Integer, nullable=False,  unique=True)
    username = db.Column(db.Unicode, nullable=False, unique=True)
    password = db.Column(db.Unicode, nullable=False)
    clid = db.Column(db.Unicode(9), nullable=False, unique=True)
    imsi = db.Column(db.Integer, nullable=False, unique=True)
    voice_balance = db.Column(db.Integer, nullable=False)
    data_balance = db.Column(db.Integer, nullable=False)

   # ki = db.Column(db.Integer)
   # city = db.Column(db.Unicode)
   # state = db.Column(db.Unicode)
   # postalcode = db.Column(db.Integer)

    def is_admin(self):
        return (level==0 if True else False)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self._id

    def VoiceBalance(self):
        return self.voice_balance

    def DataBalance(self):
        return self.data_balance

    @hybrid_property
    def VoiceBalanceHistoric(self):
        # TODO: Maybe it should use object_session
        balances = VoiceBalance.query.order_by(
            VoiceBalance._id.desc()).filter_by(from_user_id=self._id).limit(10)
        historic_list = []
        for y in balances:
            historic_list.append(row2dict(y))
        return historic_list

    @hybrid_property
    def DataBalanceHistoric(self):
        # TODO: Maybe it should use object_session
        balances = DataBalance.query.order_by(
            DataBalance._id.desc()).filter_by(user_id=self._id).limit(10)
        historic_list = []
        for y in balances:
            historic_list.append(row2dict(y))
        return historic_list

    def __init__(self, level, name, cpf, username, password, clid, imsi, voice_balance=None, data_balance=None, address=None):
        self.level = level
        self.name = name
        self.address = address
        self.cpf = cpf
        self.username = username
        self.password = password
        self.clid = clid
        self.imsi = imsi
        self.voice_balance = voice_balance
        self.data_balance = data_balance

    def __repr__(self):
        return '<User %r>' % (self.username)


class Schedules(db.Model):
    """
    # Register Credits if
    """
    __tablename__ = 'schedule'

    _id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode)
    date = db.Column(db.DateTime)

    def __init__(self, name, date):
        self.name = name
        self.date = date

    def __repr__(self):
        return 'schedule %r' % (self.name)


# this table is the association table between users and group in a
# many-to-many relationship
class ScheduleUser(db.Model):

    __tablename__ = 'schedule_user'

    user_id = db.Column(db.Integer, db.ForeignKey(
        'users._id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey(
        'schedule._id'), primary_key=True)
    count = db.Column(db.Integer, nullable=False)

    def __init__(self, user_id, group_id, count):
        self.user_id = user_id
        self.group_id = group_id
        self.count = count

    def __repr__(self):
        return 'GROUPS %r' % (self.name)


class VoiceBalance(db.Model):
    """
    Call Detail Records holds information about finished calls
    """
    __tablename__ = 'voice_balance'

    _id = db.Column(db.Integer, db.Sequence('cdr_id_seq'), primary_key=True)
    from_user_id = db.Column(
        db.Integer, db.ForeignKey('users._id'), nullable=False)
    to_user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    value = db.Column(db.Integer)
    date = db.Column(db.DateTime, nullable=False)
    origin = db.Column(db.String, nullable=False)

    # from_user = db.relationship('User', backref='originated_calls',
    #                             foreign_keys=from_user_id)
    # to_user = db.relationship('User', backref='received_calls',
    #                           foreign_keys=to_user_id)

    def __init__(self, from_user_id, value, origin, to_user_id=None, date=None):
        self.from_user_id = from_user_id
        self.to_user_id = to_user_id
        self.value = value
        self.origin = origin
        if date is not None:
            self.date = date
        else:
            self.date = datetime.now()

        user = db.session.query(User).filter_by(_id=from_user_id).first()
        user.voice_balance = user.voice_balance + int(value)

    def __repr__(self):
        return '<from=%s date=%s duration=%s>' % (self.from_user, self.date,
                                                  self.value)


# this table register the user's voice balance
class DataBalance(db.Model):

    __tablename__ = 'data_balance'

    _id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users._id'))
    date = db.Column(db.DateTime())
    value = db.Column(db.Integer)
    user_ip = db.Column(db.Unicode)
    connection_ip = db.Column(db.Unicode)
    origin = db.Column(db.Unicode, nullable=False)

    def __init__(self, user_id, value, origin, user_ip=None, connection_ip=None, date=None):

        self.user_id = user_id
        self.value = value
        self.user_ip = user_ip
        self.connection_ip = connection_ip
        self.origin = origin

        if date is not None:
            self.date = date
        else:
            self.date = datetime.now()

        user = db.session.query(User).filter_by(_id=user_id).first()
        user.data_balance = user.data_balance + int(value)

    def __repr__(self):
        return 'data_balance %r' % (self._id)


class ScheduleInput(db.Model):
    __tablename__ = 'schedule_input'

    _id = db.Column(db.Integer, primary_key=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('schedule._id'))
    voice_balance_id = db.Column(
        db.Integer, db.ForeignKey('voice_balance._id'))
    data_balance_id = db.Column(db.Integer, db.ForeignKey('data_balance._id'))

    def __init__(self, schedule_id, voice_balance_id, data_balance_id):
        self.schedule_id = schedule_id
        self.voice_balance_id = voice_balance_id
        self.data_balance_id = data_balance_id

    def __repr__(self):
        return 'schedule_input %r' % (self._id)


# Create the database tablesself.
db.create_all()
