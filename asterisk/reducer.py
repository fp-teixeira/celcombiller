#!/usr/bin/env python
"""
celcombiller AGI:
    * Consult the user balance and authorize a call
    * Save the call CDRs
    * Update the user balance
"""
# pylint: disable=C0103
from datetime import datetime
import asterisk.agi
import requests
import json

from config import ADM_USER, ADM_PSSW, URL, HEADERS

agi = asterisk.agi.AGI()


if agi.get_variable('DIALSTATUS') == 'ANSWER':
    # Time from answer to hangup
    billsec = int(agi.get_variable('CDR(billsec)'))
    # Time the user answered
    answer = datetime.fromtimestamp(float(agi.get_variable('CDR(answer,u)')))

    # Create a session
    http = requests.Session()
    # Login the session
    http.post(
        URL + '/login',
        data={'username': ADM_USER, 'password': ADM_PSSW}
    )

    url = URL + '/api/users'

    # get the from user id
    filters = [dict(name='clid', op='like', val=agi.env['agi_callerid'])]
    params = dict(q=json.dumps(dict(filters=filters)))
    response = http.get(url, params=params, headers=HEADERS)
    from_user = response.json()['objects'][0]['_id']

    # get the to user id
    filters = [dict(name='clid', op='like',
                    val=agi.get_variable('CDR(B-Number)'))]
    params = dict(q=json.dumps(dict(filters=filters)))
    response = http.get(url, params=params, headers=HEADERS)
    to_user = response.json()['objects'][0]['_id']

    payload = {'from_user_id': from_user,
               'to_user_id': to_user,
               'value': billsec * (-1),
               'origin': 'call'}
               #for some reason it doesnt work if i try to pass the date
               #'date': answer} # TODO: fix it
    # Send the request to update the user balance
    r = http.post(URL + '/api/voice_balance',
                  json=payload,
                  headers=HEADERS)
    # TODO: Handle when the request fail
    if r.ok:
        pass

    http.close()
