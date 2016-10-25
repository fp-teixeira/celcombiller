
CELCOMBiller
============

CELCOMBiller is an open source biller system to *OpenBTS* and *Asterisk*



# Used third-party libraries

* pyst
  Interface with Asterisk using either AGI or Manager interfaces
* sqlalchemy
  Database interface

# Setup developemnt enrironment

```bash
$ virtualenv -p /usr/bin/python2.7 venv
$ source venv/bin/activate
$ pip install --allow-external --allow-unverified -r requirements.txt
```

## Database setup

Each SIP user must be inserted in the database of users with a balance. The python code snippet bellow is an example of a insertion of two users.

```python
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from setup import db
from models import User, Ballance

admin = User('0','administrator', 'nowhere', '000','admin', 'adm123', '999999999','999999999999999', '0' ,'0')
guest = User('0','guest', 'nowhere', '1','guest', '123123', '999999998','999999999999998', '0' ,'0')

db.session.add(admin)
db.session.add(guest)

db.session.commit()
```

please check adduser.py



## To test api

To test the api we will use curl

###USER

you must login before test the api:

```bash
curl -c cookiefile -d "username=admin&password=adm123" -X POST -s http://localhost:5000/login
```

now to add user:

```bash
curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"level":"1", "username":"yourusername","password":"yourpassword","clid":"999999999","imsi":"12345678900", "name":"administrator","address":"lasse","cpf":"000","voice_balance":"0","data_balance":"0"}' -s http://localhost:5000/api/users
```

the balance came by another table, so we want add balance to user we need run:

add/remove data balance:

```bash
curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"value": "1000", "user_id":3,"origin":"web"}' -s http://localhost:5000/api/data_balance


#note that userId need some user id, in that case we use 1
#to remove balance the value must be negative
```

add/remove voice balance:

```bash
curl -b cookiefile -H "Content-Type: application/json" -X POST -d '{"value": "1000", "from_user_id":1, "origin":"web"}' -s http://localhost:5000/api/voice_balance

#note that userId need some user id, in that case we use 1
#to remove balance the value must be negative
```


update user

```bash
curl -X PATCH -H "Content-Type: application/json" -d '{"username":"yournewusername","password":"yournewpassowrd"}' -s http://localhost:5000/api/users/youroldusername -b cookiefile
```

remove user

```bash
curl -X DELETE -s http://localhost:5000/api/users/yourusername -b cookiefile
```

###Schedule

add group

```bash
curl -X POST -H "Content-Type: application/json" -d '{"name":"group_name","day":1, "month":1, "year":3000, "count":10}' -s http://localhost:5000/api/schedules
```

update group

```bash
curl -X PATCH -H "Content-Type: application/json" -d '{}' -s http://localost:5000/api/schedules/schedule
```


## Asterisk setup

With a working OpenBTS  Asterisk server you must modify the file /etc/asterisk/extensions-range.conf as follow:

Between the lines:

```
exten => h,             1,Log(NOTICE,A-Number=${CDR(A-Number)} A-Name=${CDR(A-Name)} A-IMSI=${CDR(A-IMSI)} B-Number=${CDR(B-Number)} B-Name=${CDR(B-Name)} B-IMSI=${CDR(B-IMSI)} hangupcause=${HANGUPCAUSE} dialstatus=${DIALSTATUS} hangupdirection=${CDR(hangupdirection)} duration=${CDR(duration)} billsec=${CDR(billsec)})

same => n,Hangup()
```

You have to write the command:

```
same =>                 n,AGI(celcombiller_reducer)   ;reduce the user balance

```


Change the line:

```
same =>                        n,Dial(SIP/${ARG1}@${ARG2}:${ARG3},${IF(${VM_INFO(${CDR(B-Number)},exists)}?${DialIMSITimeoutVM}:${DialPSTNTimeout})},g)
```

To:

```
same =>                 n,AGI(celcombiller_caller)
```



celcombiller is an AGI, implemented in the files  [celcombiller_reducer.py](celcombiller_reducer.py) and  [celcombiller_caller.py](celcombiller_caler.py),they must run in the virtual environment created in the first section. The follow files must be created in `/usr/share/asterisk/agi-bin/`  with execution permission.

celcombiller_caller
```bash
#!/bin/bash
/path_to_venv/venv/bin/python /path_to_celcombiller/celcombiller/celcombiller_caller.py
```

celcombiller_reducer
```bash
#!/bin/bash
/path_to_venv/venv/bin/python /path_to_celcombiller/celcombiller/celcombiller_reducer.py
```


## Upstart

To have Celcombiler running as a service you have to modify the file celcombiller.conf and put it in your /etc/init directory.

