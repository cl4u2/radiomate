# vim:fileencoding=utf-8:nomodified
# $Id$

# RadioMate configuration file

import logging
import os
import os.path
import sys
import imp

# Name and URL of the radio
RADIONAME = "Radio Mate"
RADIOURL = "http://radiomate.org"

# Logging
LOGFILENAME = "/tmp/radiomate.log"
LOGGINGLEVEL = logging.INFO

# Database parameters
DBHOST="127.0.0.1"
DBUSER="mate"
DBPASSWORD="radi0"
DATABASE="radiomate0"

# Seed for randomness
SEED = "pleasechangemetosomethingrandom"

# In how many minutes a session expires
SESSIONEXPIRATION = 60

# Default media file storage directory
MEDIAFILESHOMEDIR = "/opt/radiomate/media/"

# The path of the liquidsoap binary
LIQUIDSOAP = os.path.join(os.getcwd(), "../../liquidsoap-full-0.9.2/liquidsoap-0.9.2/src/liquidsoap")

# Play this if there are no transmissions
GLOBALFALLBACKPLAYLIST = 7

# Icecast server parameters, to which the stream is sent
ICECASTSERVER = "127.0.0.1"
ICECASTPORT = 8000
ICECASTPASSWORD = "hackme"
ICECASTMAINMOUNT = "radio.mp3"

# When the takeover mount is active, the radio will override current transmissions and forward its stream
TAKEOVERMOUNTURL = "http://%s:%d/takeover.mp3" % (ICECASTSERVER, ICECASTPORT)

# The mount and port used for incoming live streams
LIVESTREAMPORT = 8005
LIVESTREAMMOUNT = "live.mp3"

# The port used internally on the loopback address to communicate between jukeslot istances. 
INTERNALJUKEPORT = 8888

# Try to load the configuration from /etc/radiomateconf.py
try:
		__pathname = "/etc/radiomateconfig.py"
		if not "etcradiomateconfig" in sys.modules.keys() and os.path.isfile(__pathname):
						__m = imp.load_source("etcradiomateconfig", __pathname)
						from etcradiomateconfig import *
except:
		pass


