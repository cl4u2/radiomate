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
import shlex
import logging
from subprocess import Popen, PIPE, STDOUT
import tempfile
import os
import random

import config
import dao
from mate import TimeSlot

# dict to associate timeslot types to JukeSlot classes
JUKESLOTTYPEDICT = {}

class JukeSlotException(Exception):
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
				
				try:
						self.cm = dao.DBConnectionManager(dbhost = config.DBHOST,\
										dbuser = config.DBUSER, dbpassword = config.DBPASSWORD,\
										database = config.DATABASE)
						self.pldao = dao.PlayListDAO(self.cm)
				except Exception, e:
						raise JukeSlotException(str(e))
				
				self.plistnames = []
				
				TimeSlot.__init__(self, timeslot.dictexport())
		
		def __setattr__(self, name, value):
				Popen.__setattr__(self, name, value)
				
		def run(self):
				"inject the liquidsoap code into the spawned liquidsoap instance"
				liq = self.liquidsoapcode()
				self.logger.debug("run liquidsoap code: \n %s", liq)
				out, err = self.communicate(liq)
				self.logger.debug("output: \n %s", out)

		def getPlayListName(self, playlistid):
				"return a filename for a given playlist"
				# put the uris of the media files in a temporary file
				plistfileno, plistname = tempfile.mkstemp(prefix="radiomateplaylist", suffix=".txt", text=True)
				plistfile = os.fdopen(plistfileno, 'w')

				try:
						plist = self.pldao.getById(playlistid)
				except dao.RadioMateDAOException, e:
						raise JukeSlotException(str(e))

				if plist:
						for i, mf in enumerate(plist.mediafilelist):
								plistfile.write("%s\n" % mf.path)
								assert mf.position == i
						plistfile.write("\n")
				else:
						plistfile.close()
						raise JukeSlotException("Playlist Not Found")

				plistfile.close()

				self.logger.debug(plistname)
				self.plistnames.append(plistname)

				return plistname

		def getFallBackPlayListName(self):
				"return a filename for the fallback playlist"
				return self.getPlayListName(self.fallbackplaylist)

		def gracefulKill(self):
				"try to terminate, but if it does not work then kill"
				self.logger.debug("gracefulKill")
				if self.poll() == None:
						self.terminate()
						time.sleep(2)
				if self.poll() == None:
						self.kill()
						time.sleep(1)

		def __del__(self):
				self.gracefulKill()
				try:
						for pln in self.plistnames:
								os.remove(pln)
				except:
						pass

class MainJukeSlot(JukeSlot):
		def __init__(self):
				JukeSlot.__init__(self, timeslot=TimeSlot())
				# set the global fallback playlist
				self.fallbackplaylist = config.GLOBALFALLBACKPLAYLIST
				self.password = None
		
		def __generatePassword(self):
				"generate a random password"
				PASSLEN = 12  # password length in bytes
				numbers = range(48, 58) 
				letters = range(65, 91) + range(97, 123) 
				
				random.seed(time.time())
				passw = chr(random.choice(letters)) # must begin with a letter

				for i in range(PASSLEN-1):
						passw += chr(random.choice(letters + numbers))
				self.password = passw

		def getPassword(self):
				"get a generated password"
				if not self.password:
						self.__generatePassword()
				assert self.password
				return self.password

		def liquidsoapcode(self):
				# main liquidsoap istance, which should always be alive
				liq = """
				set("log.file.path",'/tmp/liq.log')
				set("server.telnet", false)
				set("harbor.bind_addr", "127.0.0.1")
				set("harbor.port", %d)

				#myq1 = request.create(audio=true)
				fallbackplaylist = playlist(mode="normal", '%s')

				fbacked = fallback(track_sensitive=false, [input.harbor(username = "%s", password="%s", "takeover.mp3"), input.harbor(username="mate", password="%s", "radiomate.mp3"), fallbackplaylist, blank()])

				#output.alsa(fbacked)
				output.icecast.mp3(host='%s', port = %d, password = "%s", mount = "%s", fbacked)

				""" % (config.TAKEOVERPORT, self.getFallBackPlayListName(), \
								config.TAKEOVERUSERNAME, config.TAKEOVERPASSWORD, self.getPassword(),\
								config.ICECASTSERVER, config.ICECASTPORT, config.ICECASTPASSWORD, config.ICECASTMAINMOUNT)
				#debug
				print liq
				liq = """
import time
print time.time()
print "%s"
time.sleep(60)
print "ciao"
				""" % self.getFallBackPlayListName()
				return liq


class PlayListJukeSlot(JukeSlot):
		"A simple jukeslot, with only a playlist"
		def __init__(self, timeslot, playlistid, mainpassword):
				JukeSlot.__init__(self, timeslot=timeslot)
				self.playlist = self.pldao.getById(playlistid)
				self.mainpassword = mainpassword
		
		def liquidsoapcode(self):
				liq = """
				set("log.file.path",'/tmp/pliq.log')
				set("server.telnet", false)

				plist = playlist(mode="normal", '%s')
				fallbackplist = playlist(mode="normal", '%s')

				fbacked = fallback(track_sensitive=false, [plist, fallbackplist])

				output.icecast.mp3(host='127.0.0.1', port = %d, user="mate", password = "%s", mount = "radiomate.mp3", fbacked)

				""" % (self.getPlayListName(self.playlist), self.getFallBackPlayListName(), config.TAKEOVERPORT,\
								self.mainpassword)
				return liq

JUKESLOTTYPEDICT['simpleplaylist'] = PlayListJukeSlot

