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
from models import User

agi = asterisk.agi.AGI()

from_user = User.query.filter_by(
    clid=agi.env['agi_callerid']).first()
to_user = User.query.filter_by(
    clid=agi.env['agi_extension']).first()


try:
    agi.appexec('DIAL', 'SIP/IMSI%s@127.0.0.1:5062,40,S(%d)' %
                (to_user.imsi, from_user.VoiceBalance))
except AGIAppError:
    pass
