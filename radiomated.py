#!/usr/bin/env python
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

# The RadioMate scheduling daemon

import signal
import sys
import time
from radiomate.jukebox import *

def main():
		CHECKINTERVAL = 10 

		jb = JukeBox()
				
		def termhndlr(signum, frame):
				"catch a TERM signal. Quit."
				print >> sys.stderr, "SIGTERM received."
				jb.stopcurrent()
				jb.gracefulKill()
				jb.wait()
				raise SystemExit("Quit.")

		signal.signal(signal.SIGTERM, termhndlr)
		signal.signal(signal.SIGINT, termhndlr)

		jb.run(main=True)

		while True:
				jb.selecta()
				if jb.poll(): # the main jukeslot is dead !?
						jb.run()
				time.sleep(CHECKINTERVAL)

		sys.exit(1)

main()


