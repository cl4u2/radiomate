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

# JukeSlots are played by the JukeBox. Each JukeSlot is associated to a TimeSlot
# in which a different kind of show is transmitted. For example a PlayListJukeSlot
# will transmit a playlist, while a LiveJukeSlot will accept a remote stream
# and retransmit it.

import time
import shlex
import logging
import tempfile
import os
from subprocess import Popen, PIPE, STDOUT

from .. import config
from .. import dao
from .. import mate

__all__ = ["JUKESLOTTYPEDICT", "JUKESLOTREQUIREDPARAMS", "JukeSlotException", "JukeSlot", "dao", "mate", "config"]

# dict to associate timeslot types to JukeSlot classes
JUKESLOTTYPEDICT = {}
JUKESLOTREQUIREDPARAMS = {}

class JukeSlotException(Exception):
		pass

class JukeSlot(Popen, mate.TimeSlot):
		"A TimeSlot, but with its own life."
		deathtime = 0
		def __init__(self, timeslot, mainpassword=""):
				cmd = config.LIQUIDSOAP + " -v - " # take commands from standard input 
				# spawn the process 
				Popen.__init__(self, shlex.split(cmd), bufsize=-1, universal_newlines=True, 
								stdin=PIPE, stdout=None, stderr=STDOUT)

				self.logger = logging.getLogger("radiomate.jukebox")
				logging.basicConfig(filename=config.LOGFILENAME, level=config.LOGGINGLEVEL)
				
				# initialize the connection to the database
				try:
						self.cm = dao.DBConnectionManager(dbhost = config.DBHOST,
										dbuser = config.DBUSER, dbpassword = config.DBPASSWORD,
										database = config.DATABASE)
						self.pldao = dao.PlayListDAO(self.cm)
				except Exception, e:
						raise JukeSlotException(str(e))
				
				# the list of the temporary playlist files built on the fly. 
				# Used to delete the files on JukeSlot.__del__
				self.plistnames = []
				# the password used to connect to the main JukeSlot
				self.mainpassword = mainpassword 
				
				mate.TimeSlot.__init__(self, timeslot.dictexport())
		
		def __setattr__(self, name, value):
				Popen.__setattr__(self, name, value)
				
		def run(self, main=False):
				"Inject the liquidsoap code into the spawned liquidsoap instance"
				liq = self.liquidsoapcode()
				self.logger.debug("run liquidsoap code: \n %s", liq)

				if not liq:
						return
				r = self.poll()
				if r:
						raise JukeSlotException("liquidsoap instance not running (exitcode %d)" % r)

				if main:
						# the main jukeslot forwards to the icecast server
						liq += """
						output.icecast.mp3(
							host='%s', 
							port = %d, 
							password = "%s", 
							mount = "%s", 
							restart=true, 
							description="%s", 
							url="%s", 
							radio)
						""" % (config.ICECASTSERVER, config.ICECASTPORT, config.ICECASTPASSWORD, 
										config.ICECASTMAINMOUNT, config.RADIONAME, config.RADIOURL)
						self.logger.info("Starting main liquidsoap istance")
				else:
						# the secondary jukeslots forward to the main jukeslot
						liq += """
						def rewritemeta(m) = 
							[("song", "%s - %s")]
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
						""" % (self.title, self.description, config.INTERNALJUKEPORT, self.mainpassword, self.title)
						self.logger.info("Starting secondary liquidsoap istance")

				time.sleep(1)
				self.stdin.write(liq)
				self.stdin.close()
				time.sleep(2)

				if main:
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
				try:
						return self.getPlayListName(self.fallbackplaylist)
				except:
						return self.getPlayListName(config.GLOBALFALLBACKPLAYLIST)

		def getPlayListLiquidCode(self, playlistid, playlistfilename=None):
				"""return the liquidsoap code for the given playlist. 
				If playlistfilename is given, use it, otherwise call getPlayListName()"""

				try:
						plist = self.pldao.getById(playlistid)
				except dao.RadioMateDAOException, e:
						raise JukeSlotException(str(e))

				if not plist:
						return "blank(duration=0.1)"

				if plist.random:
						pmode = "randomize"
				else:
						pmode = "normal"

				if not playlistfilename:
						playlistfilename = self.getPlayListName(playlistid)

				return 'playlist(mode="%s", "%s")' % (pmode, playlistfilename)
		
		def getFallBackPlayListLiquidCode(self):
				try:
						pn = self.getPlayListName(self.fallbackplaylist)
						return self.getPlayListLiquidCode(self.fallbackplaylist, playlistfilename=pn)
				except Exception, e:
						self.logger.debug("getFallBackPlayListLiquidCode: %s " % str(e))
				try:
						return self.getPlayListLiquidCode(config.GLOBALFALLBACKPLAYLIST)
				except Exception, e:
						self.logger.debug("getFallBackPlayListLiquidCode: %s " % str(e))
						return "blank()"
				

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

		def liquidsoapcode(self):
				"to be overridden by derived classes"
				return "\n"


