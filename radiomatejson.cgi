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
import sys
import os

MEDIAFILESHOMEDIR = "/tmp/"
FILEUPLOADKEY = 'upload'

print "Content-type: text/plain;charset=utf-8"
print 

fs = cgi.FieldStorage()
try:
		rk = fs.keys()[0]
		if rk == FILEUPLOADKEY:
				fileitem = fs[FILEUPLOADKEY]	
				bfn = os.path.basename(fileitem.filename)
				longpath = MEDIAFILESHOMEDIR + bfn 
				f = open(longpath, 'wb', 10000)
				while True:
						chunk = fileitem.file.read(10000)
						if not chunk: break
						f.write(chunk)
				f.close()
				req = None
				resp = '{"requested": "upload", "warning": null, "description": "file uploaded", "responsen": 0, "response": "ok", "path": "%s"}' % longpath
		else:
				req = fs.getfirst(rk, "no request")
except Exception:
		print fs
		raise #debug
		req = "no request"

if req:
		jp = radiomate.jsonif.JSONProcessor()
		resp = jp.process(req)

print resp

