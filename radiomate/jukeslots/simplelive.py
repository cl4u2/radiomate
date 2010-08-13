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

import random
import time
from base import *

__all__ = ["LiveJukeSlot"]

class LiveJukeSlot(JukeSlot):
		def __init__(self, timeslot, mainpassword):
				JukeSlot.__init__(self, mainpassword=mainpassword, timeslot=timeslot)
		
		def liquidsoapcode(self):
				liq = """
				#live

				set("log.file.path",'/tmp/lliq.log')
				set("server.telnet", false)
				set("harbor.bind_addr", "0.0.0.0")
				set("harbor.port", %d)  

				transfunction = fun(a,b) -> sequence([fade.final(a, type="sin"), blank(duration=1.), fade.initial(b, type="sin")])

				livestream = input.harbor(password="%s", "%s")
				
				fallbackplaylist = %s

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
				""" % (config.LIVESTREAMPORT, self.slotparams['livepassword'], config.LIVESTREAMMOUNT,
								self.getFallBackPlayListLiquidCode(), self.title, config.INTERNALJUKEPORT,
								self.mainpassword, self.title)
				return liq

JUKESLOTTYPEDICT['simplelive'] = LiveJukeSlot
