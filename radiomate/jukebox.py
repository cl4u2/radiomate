# vim:fileencoding=utf-8:nomodified
# $Id$
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

import config
import dao 
from mate import TimeSlot
from jukeslots.all import *

__all__ = ["JukeBoxException", "JukeBox"]

class JukeBoxException(Exception):
		pass

class JukeBox(MainJukeSlot):
		"Play the scheduled timeslots"
		def __init__(self):
				MainJukeSlot.__init__(self)
				self.nexttimeslot = None
				self.currenttimeslot = TimeSlot()
				self.currentjukeslot = None
				self.updatenext()

		def updatenext(self):
				"Update the next timeslot in the queue. Return True if something has changed."
				self.logger.debug("updatenext")
				
				if self.nexttimeslot: # we already have a next slot to play
						return False

				try:
						# make a new connection every time, otherwise we have an outdated view of the database
						cm = dao.DBConnectionManager(dbhost = config.DBHOST,
										dbuser = config.DBUSER, dbpassword = config.DBPASSWORD,
										database = config.DATABASE)
						tsdao = dao.TimeSlotDAO(cm)
				except Exception, e:
						raise JukeBoxException(str(e))

				curtime = time.strftime("%Y-%m-%d %H:%M:%S")
				next = tsdao.getNext(curtime)
				
				assert self.nexttimeslot == None

				if not next:
						return False
				else:
						self.nexttimeslot = next
						self.logger.info("jukebox: queueing jukeslot %d %s at %s" % (self.nexttimeslot.id,
										self.nexttimeslot.title, self.nexttimeslot.getBeginningDatetime()))
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
						jukeslotclass = JUKESLOTTYPEDICT[self.currenttimeslot.slottype]
				except KeyError:
						self.logger.error("Slot type %s not found. '%s' will be canceled." % \
										(self.currenttimeslot.slottype, self.currenttimeslot.title))
						jukeslotclass = JukeSlot

				self.logger.debug("chosen %s -> %s" % (self.currenttimeslot.slottype, jukeslotclass))
				
				try:
						# spawn a new process
						self.currentjukeslot = jukeslotclass(timeslot=self.currenttimeslot, 
										mainpassword=self.getPassword())

						self.currentjukeslot.deathtime = time.time() + self.currentjukeslot.duration*60

						self.currentjukeslot.run()
				
						if self.pollcurrent():
								self.logger.info("jukebox: playing jukeslot %d %s for %d minutes until %s" % (self.currentjukeslot.id,
												self.currentjukeslot.title, self.currentjukeslot.duration,
												time.ctime(self.currentjukeslot.deathtime)))
								return self.currentjukeslot.deathtime
						else:
								raise JukeBoxException("Process is dead.")
				except Exception, e:
						self.logger.error("jukebox: jukeslot %d %s failed. %s" % (self.currentjukeslot.id,
												self.currentjukeslot.title, str(e)))
						# update the timeslot info in the database
						try:
								cm = dao.DBConnectionManager(dbhost = config.DBHOST,
												dbuser = config.DBUSER, dbpassword = config.DBPASSWORD,
												database = config.DATABASE)
								tsdao = dao.TimeSlotDAO(cm)
								t = tsdao.getById(self.currentjukeslot.id)
								t.canceled = True
								tsdao.update(t)
								self.logger.info("jukebox: canceled show %d %s" % (self.currentjukeslot.id,
														self.currentjukeslot.title))
						except Exception, e:
								self.logger.error("jukebox: could not cancel jukeslot %d %s %s" % \
												(self.currentjukeslot.id, self.currentjukeslot.title, str(e)))

						self.currentjukeslot = None

		
		def pollcurrent(self):
				"Return False if the current JukeSlot is not alive"
				self.logger.debug("%s pollcurrent" % time.ctime())
				if not self.currentjukeslot or self.currentjukeslot.poll() != None:
						return False
				return True
		
		def stopcurrent(self, force=False):
				"Stop the current TimeSlot. If force is True, stop in any case, otherwise check the jukeslot death time"
				self.logger.debug("%s stopcurrent" % time.ctime())
				if not self.currentjukeslot:
						return True
				now = time.time()
				if force or (now >= self.currentjukeslot.deathtime):
						self.logger.info("Stopping the current jukeslot (deathtime = %s, now = %s)" % \
										(time.ctime(self.currentjukeslot.deathtime), time.ctime(now)))
						self.currentjukeslot.gracefulKill()
						self.currentjukeslot.wait()
						self.currentjukeslot = None
						return True
				return False

		def selecta(self):
				"Select the next timeslot to play, and play it if is time to do it"
				self.logger.debug("%s selecta" % time.ctime())
				
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


