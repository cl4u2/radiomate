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
from subprocess import Popen, PIPE, STDOUT
import shlex
import signal
import logging
import sys

import config
import dao 
import mate
from mate import TimeSlot

class JukeBoxException(Exception):
		pass

class JukeSlot(Popen, TimeSlot):
		"A TimeSlot, but with its own life."
		deathtime = 0
		def __init__(self, timeslot):
				# spawn the process 
				cmd = config.LIQUIDSOAP
				Popen.__init__(self, shlex.split(cmd), bufsize=-1, universal_newlines=True, 
								stdin=PIPE, stdout=PIPE, stderr=STDOUT)

				time.sleep(1)
				self.logger = logging.getLogger("radiomate.jukebox")
				logging.basicConfig(filename=config.LOGFILENAME, level=config.LOGGINGLEVEL)
				
				TimeSlot.__init__(self, timeslot.dictexport())
		
		def __setattr__(self, name, value):
				Popen.__setattr__(self, name, value)
				
		def run(self):
				"inject the liquidsoap code into the spawned liquidsoap instance"
				liq = self.liquidsoapcode()
				self.logger.debug("run liquidsoap code: \n %s", liq)
				out, err = self.communicate(liq)
				self.logger.debug("output: \n %s", out)

		def getFallBackPlaylistCode(self):
				"return the liquidsoap code for the fallback playlist"
				return """
				"""

		def gracefulKill(self):
				"try to terminate, but if it does not work then kill"
				self.logger.debug("gracefulKill")
				if self.poll() == None:
						self.terminate()
						time.sleep(2)
				if self.poll() == None:
						self.kill()
						time.sleep(1)

class MainJukeSlot(JukeSlot):
		def __init__(self):
				JukeSlot.__init__(self, timeslot=TimeSlot())

		def liquidsoapcode(self):
				# main liquidsoap code, which should always be alive
				liq = """
				set("log.file.path",'/tmp/liq.log')
				set("server.telnet",false)
				set("harbor.bind_addr","127.0.0.1")
				set("harbor.port", %d)

				myq1 = request.create(audio=true)
				myq2 = request.create(audio=true)

				fbacked = fallback(track_sensitive=false, [input.harbor(password="%s", "takeover.mp3"), request.equeue(id="myq1"), request.equeue(id="myq2"), blank()])

				#output.alsa(fbacked)
				output.icecast.mp3(host='%s', port = %d, password = "%s", mount = "%s", fbacked)

				""" % (config.TAKEOVERPORT, config.TAKEOVERPASSWORD, config.ICECASTSERVER,\
								config.ICECASTPORT, config.ICECASTPASSWORD, config.ICECASTMAINMOUNT)
				#debug
				liq = """
import time
print time.time()
time.sleep(60)
print "ciao"
				"""
				return liq

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
				self.nexttimeslot = TimeSlot()
				self.currenttimeslot = TimeSlot()
				self.currentjukeslot = None
				self.update()

		def update(self):
				"Update the next timeslot in the queue"
				self.logger.debug("update")
				curtime = time.strftime("%Y-%m-%d %H:%M:%S")
				next = self.tsdao.getNext(curtime)
				if not next or next.id != self.nexttimeslot.id:
						self.nexttimeslot = next
						return True
				else:
						return False

		def playcurrent(self):
				"Play the current TimeSlot"
				self.logger.debug("playcurrent")
				# spawn a new process
				# TODO: check timeslot type to instanciate the correct class
				self.currentjukeslot = JukeSlot(self.currenttimeslot)
				self.currentjukeslot.deathtime = time.time()/60 + js.duration
				self.currentjukeslot.run()
				return self.currentjukeslot.deathtime
		
		def pollcurrent(self):
				"Return True if the current JukeSlot is alive"
				self.logger.debug("%s pollcurrent" % time.time())
				if not self.currentjukeslot or self.currentjukeslot.poll() != None:
						return False
				return True
		
		def stopcurrent(self, force=False):
				"Stop the current TimeSlot. If force is True, stop in any case, otherwise check the jukeslot death time"
				self.logger.debug("%s stopcurrent" % time.time())
				if force or self.currentjukeslot.deathtime >= time.time()/60:
						self.currentjukeslot.gracefulKill()
						self.currentjukeslot.wait()
						self.currentjukeslot = None
						return True
				return False

		def selecta(self):
				"Select the next timeslot to play"
				self.logger.debug("%s selecta" % time.time())
				if self.update() and self.currenttimeslot == None:
						#TODO: check if currenttimeslot is playing
						self.currenttimeslot = self.nexttimeslot
				# play currenttimeslot?
				if self.currenttimeslot.getBeginningTimestamp() >= time.time() and \
								self.currenttimeslot.id != self.currentjukeslot.id and\
								self.currentjukeslot.deathtime <= time.time()/60:
						self.playcurrent()


if __name__ == "__main__":
		x = 0.1
		CHECKINTERVAL = int(60 * x)   # check every x minutes

		jb = JukeBox()

		def alarmhndlr(signum, frame):
				"catch an ALARM signal. Read the database and act consistently."
				if not jb.pollcurrent() or jb.stopcurrent():
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

		jb.run()
		jb.wait()

		print >> sys.stderr, "Program Terminated ?!"
		sys.exit(1)

