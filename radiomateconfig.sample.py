# vim:fileencoding=utf-8:nomodified
# $Id$

# RadioMate configuration file

import logging

# Name and URL of the radio
RADIONAME = "Radio Mate"
RADIOURL = "http://radiomate.org"

# Logging
LOGFILENAME = "/tmp/radiomate.log"
LOGGINGLEVEL = logging.INFO

# MySQL database parameters
DBHOST="127.0.0.1"
DBUSER="mate"
DBPASSWORD="radi0"
DATABASE="radiomate0"

# Seed for randomness
SALT = "pleasechangemetosomethingrandom"

# In how many minutes a session expires
SESSIONEXPIRATION = 60

# Default media file storage directory
MEDIAFILESHOMEDIR = "/opt/radiomate/media/"

# The path of the liquidsoap binary
LIQUIDSOAP = "/usr/local/bin/liquidsoap"

# Play this if there are no transmissions
GLOBALFALLBACKPLAYLIST = 1

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

