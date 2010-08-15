#!/usr/bin/env python
# vim:fileencoding=utf-8:nomodified
# $Id$

import time
from radiomate.dao import *
from radiomate.mate import *

# connection parameters
DBHOST="127.0.0.1"
DBUSER="mate"
DBPASSWORD="radi0"
DATABASE="radiomate0"

cm = DBConnectionManager(
				dbhost = DBHOST, 
				dbuser = DBUSER,
				dbpassword = DBPASSWORD,
				database = DATABASE
				)

def newPlayListSlot():
		tsdao = TimeSlotDAO(cm)
		ts = TimeSlot()
		ts.creator = 'foobar'
		ts.slottype = 'simpleplaylist'
		ts.slotparams = {'playlistid': 8}
		st = time.localtime(time.time() + 60)
		ts.beginningtime = {'year': st[0], 'month': st[1], 'day': st[2], 'hour': st[3], 'minute': st[4]}
		ts.duration = 2
		ts.title = "The Test Show"
		ts.description = "the best test show ever"
		ts.comment = "just a test"
		ts.tags = "test, show, radio"
		ts.fallbackplaylist = 9
		print ts.beginningtime
		print ts
		tsdao.insert(ts)

def newLiveSlot():
		tsdao = TimeSlotDAO(cm)
		ts = TimeSlot()
		ts.creator = 'foobar'
		ts.slottype = 'simplelive'
		#ts.slottype = 'alienslot'
		ts.slotparams = {'livepassword': 'ciao'}
		st = time.localtime(time.time() + 60)
		ts.beginningtime = {'year': st[0], 'month': st[1], 'day': st[2], 'hour': st[3], 'minute': st[4]}
		ts.duration = 2
		ts.title = "The Live Test Show"
		ts.description = "the best test show ever"
		ts.comment = "just a test"
		ts.tags = "test, show, radio"
		ts.fallbackplaylist = 9
		print ts.beginningtime
		print ts
		tsdao.insert(ts)

#newPlayListSlot()
newLiveSlot()


