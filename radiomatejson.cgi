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

import cgi
import radiomate.jsonif
import sys

import cgitb
cgitb.enable()

print "Content-type: text/plain;charset=utf-8"
print 

fs = cgi.FieldStorage()
try:
		rk = fs.keys()[0]
		req = fs.getfirst(rk, "no request")
except:
		req = "no request"

jp = radiomate.jsonif.JSONProcessor()
resp = jp.process(req)

print resp

