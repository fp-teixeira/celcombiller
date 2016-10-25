from config import db
from models import User


admin = User('0', 'administrator', '000', 'admin', 'adm123',
             '999999999', '999999999999999', '0', '0', 'nowhere')
guest = User('3', 'guest', '1', 'guest', '123123', '999999998',
             '999999999999998', '0', '0', 'nowhere')

db.session.add(admin)
db.session.add(guest)

db.session.commit()
