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

# JukeSlots are played by the JukeBox. Each JukeSlot is associated to a TimeSlot
# in which a different kind of show is transmitted. For example a PlayListJukeSlot
# will transmit a playlist, while a LiveJukeSlot will accept a remote stream
# and retransmit it.

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
		def __init__(self, timeslot, mainpassword=""):
				cmd = config.LIQUIDSOAP + " -v - " # take commands from standard input 
				# spawn the process 
				Popen.__init__(self, shlex.split(cmd), bufsize=-1, universal_newlines=True, 
								stdin=PIPE, stdout=PIPE, stderr=STDOUT)

				time.sleep(1)
				self.logger = logging.getLogger("radiomate.jukebox")
				logging.basicConfig(filename=config.LOGFILENAME, level=config.LOGGINGLEVEL)
				
				# initialize the connection to the database
				try:
						self.cm = dao.DBConnectionManager(dbhost = config.DBHOST,\
										dbuser = config.DBUSER, dbpassword = config.DBPASSWORD,\
										database = config.DATABASE)
						self.pldao = dao.PlayListDAO(self.cm)
				except Exception, e:
						raise JukeSlotException(str(e))
				
				# the list of the temporary playlist files built on the fly. 
				# Used to delete the files on JukeSlot.__del__
				self.plistnames = []
				# the password used to connect to the main JukeSlot
				self.mainpassword = mainpassword 
				
				TimeSlot.__init__(self, timeslot.dictexport())
		
		def __setattr__(self, name, value):
				Popen.__setattr__(self, name, value)
				
		def run(self):
				"Inject the liquidsoap code into the spawned liquidsoap instance"
				liq = self.liquidsoapcode()
				self.logger.debug("run liquidsoap code: \n %s", liq)
				r = self.poll()
				if r:
						raise JukeSlotException("liquidsoap instance not running (exitcode %d)" % r)

				out, err = self.communicate(liq)
				self.logger.debug("output: \n %s", out)

				r = self.poll()
				if r:
						raise JukeSlotException("liquidsoap istance not running (exitcode %d)" % r)

		def getPlayListName(self, playlistid):
				"Build a playlist file on the fly and return its filename"

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
		"The main jukeslot, to which others connect"
		def __init__(self):
				JukeSlot.__init__(self, timeslot=TimeSlot(), mainpassword="")
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
				# main liquidsoap istance
				set("log.file.path",'/tmp/liq.log')
				set("server.telnet", false)
				set("harbor.bind_addr", "127.0.0.1")
				set("harbor.port", %d)  

				transfunction = fun(a,b) -> sequence([fade.final(a, type="sin"), blank(duration=2.), fade.initial(b, type="sin")])

				fallbackplaylist = playlist(mode="normal", '%s')

				radiomate = input.harbor(password="%s", "radiomate.mp3")

				takeover = input.http("%s")

				radio = fallback(track_sensitive=false,
					[takeover, radiomate, fallbackplaylist, blank()],
					transitions = [transfunction, transfunction, transfunction, transfunction]
					)

				output.icecast.mp3(
					host='%s', 
					port = %d, 
					password = "%s", 
					mount = "%s", 
					restart=true, 
					description="%s", 
					url="%s", 
					radio)

				""" % (config.INTERNALJUKEPORT, self.getFallBackPlayListName(), self.getPassword(), 
								config.TAKEOVERMOUNTURL, config.ICECASTSERVER, config.ICECASTPORT, 
								config.ICECASTPASSWORD, config.ICECASTMAINMOUNT, config.RADIONAME, 
								config.RADIOURL)
				self.logger.info("Starting main liquidsoap istance")
				return liq


class PlayListJukeSlot(JukeSlot):
		"A simple jukeslot, with only a playlist"
		def __init__(self, timeslot, mainpassword):
				JukeSlot.__init__(self, mainpassword, timeslot=timeslot)
				playlistid = self.slotparams['playlistid']
				self.playlist = self.pldao.getById(playlistid)
		
		def liquidsoapcode(self):
				liq = """
				# playlist
				set("log.file.path",'/tmp/pliq.log')
				set("server.telnet", false)
				
				transfunction = fun(a,b) -> sequence([fade.final(a, type="sin"), blank(duration=2.), fade.initial(b, type="sin")])

				plist = playlist(mode="normal", '%s')

				fallbackplist = playlist(mode="normal", '%s')

				radio = fallback(track_sensitive=false, 
						[plist, fallbackplist, blank()],
						transitions=[transfunction, transfunction, transfunction]
						)

				output.icecast.mp3(
						host='127.0.0.1', 
						port = %d, 
						password = "%s", 
						mount = "radiomate.mp3", 
						radio)

				""" % (self.getPlayListName(self.playlist), self.getFallBackPlayListName(),\
								config.INTERNALJUKEPORT, self.mainpassword)
				self.logger.info("Starting playlist jukeslot")
				return liq

JUKESLOTTYPEDICT['simpleplaylist'] = PlayListJukeSlot


class LiveJukeSlot(JukeSlot):
		def __init__(self, timeslot, mainpassword):
				JukeSlot.__init__(self, mainpassword, timeslot=timeslot)
		
		def liquidsoapcode(self):
				liq = """
				#live

				set("log.file.path",'/tmp/lliq.log')
				set("server.telnet", false)
				set("harbor.bind_addr", "0.0.0.0")
				set("harbor.port", %d)  

				transfunction = fun(a,b) -> sequence([fade.final(a, type="sin"), blank(duration=1.), fade.initial(b, type="sin")])

				livestream = input.harbor(password="%s", "live.mp3")
				
				fallbackplist = playlist(mode="normal", '%s')

				radio = fallback(track_sensitive=false, 
						[livestream, fallbackplaylist, blank()], 
						transitions=[transfunction, transfunction, transfunction])
				
				def rewritemeta(m) = 
					[("song", "%s")]
				end
				radio = map_metadata(rewritemeta, radio)
				
				output.icecast.mp3(
					host='127.0.0.1', 
					port = %d, 
					password = "%s", 
					mount = "radiomate.mp3", 
					restart=true, 
					description="%s",
					radio)
				""" % (self.LIVESTREAMPORT, self.slotparams['livepassword'], self.getFallBackPlayListName(), \
								self.title, self.INTERNALJUKEPORT, self.mainpassword, self.title)
				return liq

JUKESLOTTYPEDICT['simplelive'] = LiveJukeSlot

