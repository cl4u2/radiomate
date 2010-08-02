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
import config
from mate import *
from dao import *

# The JSON interface 

class RadioMateJSONError(Exception):
		"JSON API generic error"
		pass


class RadioMateJSONSyntaxError(Exception):
		"JSON syntax error"
		pass


RESPONSE_OK = 0
RESPONSE_NOTALLOWED = 101
RESPONSE_DONTEXISTS = 201
RESPONSE_ALREADYEXISTS = 202
RESPONSE_SERVERERROR = 301
RESPONSE_REQERROR = 401
RESPONSE_ERROR = 501

ERRORDICT = {
				RESPONSE_OK: "ok",
				RESPONSE_NOTALLOWED: "notallowed",
				RESPONSE_ALREADYEXISTS: "alreadyexists",
				RESPONSE_DONTEXISTS: "dontexists",
				RESPONSE_SERVERERROR: "servererror",
				RESPONSE_REQERROR: "requesterror",
				RESPONSE_ERROR: "error"
}


class RadioMateJSONRequest(dict):
		def __init__(self, jsonstring):
				dict.__init__(self)
				try:
						reqdict = json.loads(jsonstring)
						#TODO: validate the request
						self.update(reqdict)
				except Exception, e:
						raise RadioMateJSONSyntaxError(str(e))



class RadioMateJSONResponse(dict):
		def __init__(self, responsen, description, responsedict = {}):
				dict.__init__(self)
				try:
						dict.__setitem__(self, 'responsen', responsen)
						dict.__setitem__(self, 'response', ERRORDICT[responsen])
						dict.__setitem__(self, 'description', description)
						self.update(responsedict)
				except Exception, e:
						raise RadioMateJSONError(str(e))

		def dumps(self):
				return json.dumps(self, skipkeys=True)
		

class RadioMateJSONProcessor(object):
		"Process JSON requests and return JSON responses, through the process() function"
		def __init__(self):
				"set up the connection to the database"
				try:
						self.connectionmanager = DBConnectionManager(
										dbhost = config.DBHOST, 
										dbuser = config.DBUSER,
										dbpassword = config.DBPASSWORD,
										database = config.DATABASE
										)
				except Exception, e:
						raise RadioMateJSONError(str(e))
		
		def process(self, request):
				"select the appropriate handler for the request"
				try:
						req = RadioMateJSONRequest(request)
				except Exception, e:
						response = RadioMateJSONResponse(RESPONSE_REQERROR, "Incorrect JSON Request [%s]" % str(e))
						return response.dumps()

				# validate username and password
				try:
						userdao = UserDAO(self.connectionmanager)
						username = req['username']
						password = req['password']
						requser = userdao.logincheck(username, password)
						if not requser: raise RadioMateJSONError("Login Error")
				except Exception, e:
						response = RadioMateJSONResponse(RESPONSE_NOTALLOWED, "Incorrect Login [%s]" % str(e))
						return response.dumps()

				# TODO: implement password changing
				
				# small python magic to call the method that has the same name of the request
				if req.has_key('request') and (req['request'] in self.__class__.__dict__):
						response = self.__class__.__dict__[req['request']](self, requser, req)
				else:
						response = RadioMateJSONResponse(RESPONSE_REQERROR, "Incorrect JSON Request")

				return response.dumps()
				
		def createrole(self, requser, req):
				rd = {'requested': "createrole", 'role': None}
				if not requser.role.canManageRoles:
						return RadioMateJSONResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						r = Role(req['role'])
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						rcheck = roledao.getByName(r.rolename)
				except RadioMateDAOException, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				if rcheck:
						return RadioMateJSONResponse(RESPONSE_ALREADYEXISTS, "Role already exists", rd)

				try:
						res = roledao.insert(r)
						rcheck = roledao.getByName(r.rolename)
						if res and rcheck:
								rd['role'] = rcheck.dictexport()
								return RadioMateJSONResponse(RESPONSE_OK, "Role created", rd)
				except RadioMateDAOException, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)
				except Exception, e:
						pass
				return RadioMateJSONResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def editrole(self, requser, req):
				rd = {'requested': "editrole", 'role': None}
				if not requser.role.canManageRoles:
						return RadioMateJSONResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						assert req['role']
						rolename = req['role']['rolename']
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not r:
						return RadioMateJSONResponse(RESPONSE_DONTEXISTS, "Role %s not found" % rolename, rd)

				# edit the role
				try:
						r.__dict__.update(req['role'])
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				try:
						res = roledao.update(r)
						rcheck = roledao.getByName(r.rolename)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res and rcheck:
						rd['role'] = rcheck.dictexport()
						return RadioMateJSONResponse(RESPONSE_OK, "Role successfully edited", rd)
				else:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def removerole(self, requser, req):
				rd = {'requested': "removerole", 'rolename': None}
				if not requser.role.canManageRoles:
						return RadioMateJSONResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						rolename = req['rolename']
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not r:
						return RadioMateJSONResponse(RESPONSE_DONTEXISTS, "Role %s not found" % rolename, rd)

				# remove the role
				try:
						res = roledao.removeByName(rolename)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res:
						rd['rolename'] = rolename
						return RadioMateJSONResponse(RESPONSE_OK, "Role has been removed", rd)
				else:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def getrole(self, requser, req):
				rd = {'requested': "getrole", 'role': None}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						rolename = req['rolename']
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not isinstance(r, Role):
						return RadioMateJSONResponse(RESPONSE_DONTEXISTS, "Role %s not found" % rolename, rd)
				
				rd['role'] = r.dictexport()
				return RadioMateJSONResponse(RESPONSE_OK, "Role found", rd)
		
		def listroles(self, requser, req):
				rd = {'requested': "listroles", 'listlength':0, 'rolelist': []}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				try:
						rlist = roledao.getAll()
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				rolelist = []
				for r in rlist:
						try:
								rolelist.append(r.dictexport())
						except Exception, e:
								return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				rd['listlength'] = len(rlist)
				rd['rolelist'] = rolelist
				return RadioMateJSONResponse(RESPONSE_OK, "Role list retrieved", rd)

		def createuser(self, requser, req):
				rd = {'requested': "createuser", 'user': None}
				if not requser.role.canManageUsers:
						return RadioMateJSONResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)
				try:
						u = User(req['user'])
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						ucheck = userdao.getByName(u.name)
				except RadioMateDAOException, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				if ucheck:
						return RadioMateJSONResponse(RESPONSE_ALREADYEXISTS, "User already exists", rd)

				try:
						roledao = RoleDAO(self.connectionmanager)
						rcheck = roledao.getByName(u.rolename)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				if not rcheck:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Role %s does not exist" % u.rolename, rd)

				try:
						res = userdao.insert(u)
						ucheck = userdao.getByName(u.name)
						if res and ucheck:
								rd['user'] = ucheck.dictexport()
								return RadioMateJSONResponse(RESPONSE_OK, "User successfully created", rd)
				except RadioMateDAOException, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)
				except Exception, e:
						pass
				return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

		def edituser(self, requser, req):
				rd = {'requested': "edituser", 'user': None}
				if not requser.role.canManageUsers:
						return RadioMateJSONResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						assert req['user']
						username = req['user']['name']
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						u = userdao.getByName(username)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not u:
						return RadioMateJSONResponse(RESPONSE_DONTEXISTS, "User %s not found" % username, rd)

				# edit the user
				try:
						u.__dict__.update(req['user'])
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				try:
						res = userdao.update(u)
						ucheck = userdao.getByName(u.name)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res and ucheck:
						rd['user'] = ucheck.dictexport()
						return RadioMateJSONResponse(RESPONSE_OK, "User successfully edited", rd)
				else:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Unknown Error", rd)
		
		def removeuser(self, requser, req):
				rd = {'requested': "removeuser", 'name': None}
				if not requser.role.canManageUsers:
						return RadioMateJSONResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						username = req['name']
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						u = userdao.getByName(username)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not u:
						return RadioMateJSONResponse(RESPONSE_DONTEXISTS, "User %s not found" % username, rd)

				# remove the user
				try:
						res = userdao.removeByName(username)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res:
						rd['name'] = username
						return RadioMateJSONResponse(RESPONSE_OK, "User has been removed", rd)

				else:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def getuser(self, requser, req):
				rd = {'requested': "getuser", 'user': None}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						username = req['name']
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						u = userdao.getByName(username)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not isinstance(u, User):
						return RadioMateJSONResponse(RESPONSE_DONTEXISTS, "User %s not found" % username, rd)
				
				rd['user'] = u.dictexport()
				return RadioMateJSONResponse(RESPONSE_OK, "User found", rd)

		def listusers(self, requser, req):
				rd = {'requested': "listusers", 'listlength': 0, 'userlist': []}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						ulist = userdao.getAll()
				except Exception, e:
						return RadioMateJSONResponse(RESPONSE_SERVERERROR, str(e), rd)

				userlist = []
				for u in ulist:
						try:
								userlist.append(u.dictexport())
						except Exception, e:
								return RadioMateJSONResponse(RESPONSE_ERROR, str(e), rd)

				rd['listlength'] = len(ulist)
				rd['userlist'] = userlist
				return RadioMateJSONResponse(RESPONSE_OK, "User list retrieved", rd)

		def registerfile(self, requser, req):
				pass

		def searchfiles(self, requser, req):
				pass

		def editfile(self, requser, req):
				pass

		def createplaylist(self, requser, req):
				pass

		def editplaylist(self, requser, req):
				pass

		def addfilestoplaylist(self, requser, req):
				pass

		def removefilesfromplaylist(self, requser, req):
				pass

		def switchfilesinplaylist(self, requser, req):
				pass

		def listuserplaylists(self, requser, req):
				pass

		def createtimeslot(self, requser, req):
				pass

		def edittimeslot(self, requser, req):
				pass

		def listtimeslots(self, requser, req):
				pass

		def createtestslot(self, requser, req):
				pass

		def listnetcasts(self, requser, req):
				pass

		

						
