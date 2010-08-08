# RadioMate configuration file

import logging
import os
import os.path

LOGFILENAME = "/tmp/radiomate.log"
LOGGINGLEVEL = logging.DEBUG

DBHOST="127.0.0.1"
DBUSER="mate"
DBPASSWORD="radi0"
DATABASE="radiomate0"

MEDIAFILESHOMEDIR = "/tmp/"

#LIQUIDSOAP = os.path.join(os.getcwd(), "../../../liquidsoap-full-0.9.2/liquidsoap-0.9.2/src/liquidsoap")
LIQUIDSOAP = "/usr/bin/python"   #debug

TAKEOVERUSERNAME = "takeover"
TAKEOVERPASSWORD = "crackme"
TAKEOVERPORT = 8005

GLOBALFALLBACKPLAYLIST = 7

ICECASTSERVER = "127.0.0.1"
ICECASTPORT = 8000
ICECASTPASSWORD = "hackme"
ICECASTMAINMOUNT = "main.mp3"


