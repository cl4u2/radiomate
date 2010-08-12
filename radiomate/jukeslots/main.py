# vim:fileencoding=utf-8:nomodified
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

import random
import time
from base import *

from .. import config

__all__ = ["MainJukeSlot"]

class MainJukeSlot(JukeSlot):
		"The main jukeslot, to which others connect"
		def __init__(self):
				JukeSlot.__init__(self, timeslot=mate.TimeSlot(), mainpassword="")
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

