#!/usr/bin/env python
# vim:fileencoding=utf-8:syntax=python:nomodified
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

import cgitb
cgitb.enable()

import cgi
import radiomate.jsonif
from radiomate.config import MEDIAFILESHOMEDIR
import sys
import os

FILEUPLOADKEY = 'upload'

print "Content-type: text/plain;charset=utf-8"
print 

req = None
fs = cgi.FieldStorage()
try:
		rk = fs.keys()[0]
		if rk == FILEUPLOADKEY:
				fileitem = fs[FILEUPLOADKEY]	
				bfn = os.path.basename(fileitem.filename)
				longpath = MEDIAFILESHOMEDIR + "/" + bfn 
				if os.path.exists(longpath):
						resp = '{"requested": "upload", "warning": "file already exists", "description": "file not uploaded", "responsen": 202, "response": "alreadyexists", "path": "%s"}' % longpath
				else:
						f = open(longpath, 'wb', 10000)
						while True:
								chunk = fileitem.file.read(10000)
								if not chunk: break
								f.write(chunk)
						f.close()
						resp = '{"requested": "upload", "warning": null, "description": "file uploaded", "responsen": 0, "response": "ok", "path": "%s"}' % longpath
		else:
				req = fs.getfirst(rk, "no request")
except Exception,e:
		raise
		req = "no request"

if req:
		jp = radiomate.jsonif.JSONProcessor()
		resp = jp.process(req)

print resp

