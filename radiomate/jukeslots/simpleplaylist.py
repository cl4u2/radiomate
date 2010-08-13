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

__all__ = ["PlayListJukeSlot"]

class PlayListJukeSlot(JukeSlot):
		"A simple jukeslot, with only a playlist"
		def __init__(self, timeslot, mainpassword):
				JukeSlot.__init__(self, mainpassword=mainpassword, timeslot=timeslot)
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

				""" % (self.getPlayListName(self.playlist.id), self.getFallBackPlayListName(),
								config.INTERNALJUKEPORT, self.mainpassword)
				self.logger.info("Starting playlist jukeslot")
				return liq

JUKESLOTTYPEDICT['simpleplaylist'] = PlayListJukeSlot

