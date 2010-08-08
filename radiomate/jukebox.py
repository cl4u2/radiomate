#
#  Copyright 2010 Claudio Pisa (clauz at ninux dot org)
#
#  This file is part of RadioMate
#
#  RadioMate is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  RadioMate is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with RadioMate.  If not, see <http://www.gnu.org/licenses/>.
#

import time
import signal
import sys

import config
import dao 
from mate import TimeSlot
from jukeslots import *


class JukeBoxException(Exception):
		pass

class JukeBox(MainJukeSlot):
		"Play the scheduled timeslots"
		def __init__(self):
				MainJukeSlot.__init__(self)
				try:
						self.tsdao = dao.TimeSlotDAO(dao.DBConnectionManager(dbhost = config.DBHOST,\
										dbuser = config.DBUSER, dbpassword = config.DBPASSWORD,\
										database = config.DATABASE))
				except Exception, e:
						raise JukeBoxException(str(e))
				self.nexttimeslot = None
				self.currenttimeslot = TimeSlot()
				self.currentjukeslot = None
				self.updatenext()

		def updatenext(self):
				"Update the next timeslot in the queue. Return True if something has changed."
				self.logger.debug("updatenext")
				
				if self.nexttimeslot: # we already have a next slot to play
						return False

				curtime = time.strftime("%Y-%m-%d %H:%M:%S")
				next = self.tsdao.getNext(curtime)
				
				assert self.nexttimeslot == None

				if not next:
						return False
				else:
						self.nexttimeslot = next
						return True

		def clearnext(self):
				"Drop the next slot to be played"
				self.logger.debug("clearnext")
				self.nexttimeslot = None

		def playcurrent(self):
				"Play the current TimeSlot"
				self.logger.debug("playcurrent")
				self.logger.debug("%s" % JUKESLOTTYPEDICT)
				# check timeslot type to instanciate the correct class
				try:
						jukeslotclass = JUKESLOTTYPEDICT[timeslot.type]
				except KeyError:
						jukeslotclass = JukeSlot
				
				# spawn a new process
				self.currentjukeslot = jukeslotclass(self.currenttimeslot)

				self.currentjukeslot.deathtime = time.time()/60 + js.duration
				self.currentjukeslot.run()
				return self.currentjukeslot.deathtime
		
		def pollcurrent(self):
				"Return False if the current JukeSlot is not alive"
				self.logger.debug("%s pollcurrent" % time.time())
				if not self.currentjukeslot or self.currentjukeslot.poll() != None:
						return False
				return True
		
		def stopcurrent(self, force=False):
				"Stop the current TimeSlot. If force is True, stop in any case, otherwise check the jukeslot death time"
				self.logger.debug("%s stopcurrent" % time.time())
				if not self.currentjukeslot:
						return True
				if force or self.currentjukeslot.deathtime >= time.time()/60:
						self.currentjukeslot.gracefulKill()
						self.currentjukeslot.wait()
						self.currentjukeslot = None
						return True
				return False

		def selecta(self):
				"Select the next timeslot to play, and play it if is time to do it"
				self.logger.debug("%s selecta" % time.time())
				
				if not self.pollcurrent(): # check if the current jukeslot is dead 
						self.stopcurrent(force=True) # the process is dead! Be sure to kill it.
				else: 
						self.stopcurrent() # check if its time to stop the current jukeslot

				self.updatenext() # update the next slot to be played 
						
				if not self.nexttimeslot: # no next slot
						return # nothing to play

				# time to play the next timeslot?
				if self.nexttimeslot.getBeginningTimestamp() <= time.time():
						# time to start
						self.stopcurrent(force=True) # next slot's turn. kill the current jukeslot
						self.currenttimeslot = self.nexttimeslot # put the next slot in place
						self.clearnext()
						self.playcurrent() # play


if __name__ == "__main__":
		x = 0.1
		CHECKINTERVAL = int(60 * x)   # check every x minutes

		jb = JukeBox()

		def alarmhndlr(signum, frame):
				"catch an ALARM signal. Read the database and act consistently."
				jb.selecta()
				signal.alarm(CHECKINTERVAL)

		def huphndlr(signum, frame):
				"catch an HUP signal. Force reread of the database."
				assert signum == signal.SIGHUP
				signal.alarm(0)
				alarmhndlr(signum, frame)

		def termhndlr(signum, frame):
				"catch a TERM signal. Quit."
				print >> sys.stderr, "SIGTERM received."
				jb.gracefulKill()
				jb.wait()
				raise SystemExit("Quit.")

		signal.signal(signal.SIGALRM, alarmhndlr)
		signal.signal(signal.SIGHUP, huphndlr)
		signal.signal(signal.SIGTERM, termhndlr)
		signal.signal(signal.SIGINT, termhndlr)

		huphndlr(signal.SIGHUP, None)

		#debug
		jb.run()
		#try:
		#		jb.run()
		#except Exception, e:
		#		raise SystemExit(str(e))

		jb.wait()

		print >> sys.stderr, "Program Terminated ?!"
		sys.exit(1)

