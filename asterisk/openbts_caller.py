#!/usr/bin/env python
"""
celcombiller AGI:
    * Consult the user balance and authorize a call
    * Save the call CDRs
    * Update the user balance
"""
# pylint: disable=C0103
import asterisk.agi
from asterisk.agi import AGIAppError
from config import ADM_USER, ADM_PSSW, URL, HEADERS, RING_TIME
import requests
import json

agi = asterisk.agi.AGI()
http = requests.Session()

http.post(
    URL + '/login',
    data={'username': ADM_USER, 'password': ADM_PSSW}
)

url = URL + '/api/users'

filters = [dict(name='clid', op='eq', val=agi.env['agi_callerid'])]
params = dict(q=json.dumps(dict(filters=filters)))
response = http.get(url, params=params, headers=HEADERS)
time = response.json()['objects'][0]['voice_balance']

filters = [dict(name='clid', op='eq', val=agi.env['agi_extension'])]
params = dict(q=json.dumps(dict(filters=filters)))
response = http.get(url, params=params, headers=HEADERS)
receptor = response.json()['objects'][0]['imsi']

try:
    agi.appexec('DIAL', 'SIP/IMSI%s@127.0.0.1:5062,%d,S(%d)' %
                (receptor, RING_TIME, time))
except AGIAppError:
    pass

http.close()
