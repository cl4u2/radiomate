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

import json
from mate import *
from dao import *

# The JSON interface 

class RadioMateJSONError(Exception):
		"JSON API generic error"
		pass


class RadioMateJSONSyntaxError(Exception):
		"JSON syntax related error"
		pass


class RadioMateJSONProcessor(object):
		"Process JSON requests and return JSON responses, through the process() function"

		def __init__(self):
				"set up the connection to the database"
				#TODO: move parameters to config file
				DBHOST="127.0.0.1"
				DBUSER="mate"
				DBPASSWORD="radi0"
				DATABASE="radiomate0"
				self.connectionmanager = DBConnectionManager(
								dbhost = DBHOST, 
								dbuser = DBUSER,
								dbpassword = DBPASSWORD,
								database = DATABASE
								)
		
		def process(self, request):
				"select the appropriate handler for the request"
				try:
						req = json.loads(request)
				except ValueError, e:
						raise RadioMateJSONSyntaxError(e.args)

				#TODO: validate username and password

				# python magic
				if req['request'] in self.__class__.__dict__:
						dictresponse = self.__class__.__dict__[req['request']](self, req)
				else:
						raise RadioMateJSONError("Incorrect JSON request")

				response = json.dumps(dictresponse)

				return response
				
		def createrole(self, req):
				responsed = {}
				try:
						r = Role(req["role"])
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] = 4
						responsed['description'] = str(e)
						responsed['role'] = req['role']
						return responsed

				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] = 3
						responsed['description'] = str(e)
						responsed['role'] = req['role']
						return responsed

				try:
						res = roledao.insert(r)
						if res:
								responsed['response'] = "rolecreated"
								responsed['responsen'] = 0
								responsed['description'] = "O.K."
				except RadioMateDAOException, e:
						responsed['response'] = "alreadyexists"
						responsed['responsen'] = 2
						responsed['description'] = str(e)
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] = 4
						responsed['description'] = str(e)
				responsed['role'] = r.__dict__
				return responsed


		def editrole(self, req):
				pass

		def createuser(self, req):
				pass

		def edituser(self, req):
				pass

		def listusers(self, req):
				pass

		def registerfile(self, req):
				pass

		def searchfiles(self, req):
				pass

		def editfile(self, req):
				pass

		def createplaylist(self, req):
				pass

		def editplaylist(self, req):
				pass

		def addfilestoplaylist(self, req):
				pass

		def removefilesfromplaylist(self, req):
				pass

		def switchfilesinplaylist(self, req):
				pass

		def listuserplaylists(self, req):
				pass

		def createtimeslot(self, req):
				pass

		def edittimeslot(self, req):
				pass

		def listtimeslots(self, req):
				pass

		def createtestslot(self, req):
				pass

		def listnetcasts(self, req):
				pass

		

						



if __name__ == "__main__":
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"password": "secret",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": false,
				"canRegisterFiles": false,
				"canManageRegisteredFiles": false,
				"canSearchRegisteredFiles": false,
				"canManageTimetable": false,
				"fixedSlotTime": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": 60,
				"canCreateTestMountpoint": false,
				"canListNetcasts": false
			}
		}
		"""
		print jsonrequest
		jp = RadioMateJSONProcessor()
		r = jp.process(jsonrequest)
		print r

