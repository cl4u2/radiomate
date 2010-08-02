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
		"JSON syntax related error"
		pass

#TODO: change error numeration from 1,2,3,4,5 to 10,20,30,40,50
RESPONSE_OK = 0
RESPONSE_NOTALLOWED = 1
RESPONSE_EXISTANCE = 2
RESPONSE_SERVERERROR = 3
RESPONSE_ERROR = 4
RESPONSE_REQERROR = 4

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
						req = json.loads(request)
				except ValueError, e:
						raise RadioMateJSONSyntaxError(e.args)

				# validate username and password
				try:
						userdao = UserDAO(self.connectionmanager)
						username = str(req['username'])
						password = str(req['password'])
						requser = userdao.logincheck(username, password)
						if not requser: raise RadioMateJSONError("Login Error")
				except Exception, e:
						dictresponse = {
										'response': "notallowed", 
										'responsen': RESPONSE_NOTALLOWED, 
										'description': "Incorrect Login [%s]" % str(e)
										}
						response = json.dumps(dictresponse, skipkeys=True)
						return response

				# TODO: implement password changing
				
				# small python magic
				if req.has_key('request') and (req['request'] in self.__class__.__dict__):
						dictresponse = self.__class__.__dict__[req['request']](self, requser, req)
				else:
						dictresponse = {
										'response': "error", 
										'responsen': RESPONSE_REQERROR, 
										'description': "Incorrect JSON request",
										'request': req
										}

				response = json.dumps(dictresponse, skipkeys=True)
				return response
				
		def createrole(self, requser, req):
				if not requser.role.canManageRoles:
						responsed = {
										'response': "notallowed", 
										'responsen':  RESPONSE_NOTALLOWED,
										'description': "User role does not allow this action",
										'role': None
										}
						return responsed

				responsed = {
								'response': "error", 
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'role': None
								}
				try:
						r = Role(req['role'])
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				try:
						rcheck = roledao.getByName(r.rolename)
				except RadioMateDAOException, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				if rcheck:
						responsed['response'] = "alreadyexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "Role already exists"
						responsed['role'] = None
						return responsed

				try:
						res = roledao.insert(r)
						rcheck = roledao.getByName(r.rolename)
						if res and rcheck:
								responsed['response'] = "rolecreated"
								responsed['responsen'] =  RESPONSE_OK
								responsed['description'] = "O.K."
								responsed['role'] = rcheck.dictexport()
								return responsed
				except RadioMateDAOException, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed
				except Exception, e:
						pass
				responsed['response'] = "error"
				responsed['responsen'] =  RESPONSE_ERROR
				responsed['description'] = "Unknown Error"
				responsed['role'] = None
				return responsed

		def editrole(self, requser, req):
				if not requser.role.canManageRoles:
						responsed = {
										'response': "notallowed", 
										'responsen':  RESPONSE_NOTALLOWED,
										'description': "User role does not allow this action",
										'role': None
										}
						return responsed
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'role': None
								}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				try:
						assert req['role']
						rolename = req['role']['rolename']
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Check JSON Syntax [%s]" % str(e)
						responsed['role'] = None
						return responsed

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				if r == None:
						responsed['response'] = "dontexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "Role %s not found" % rolename
						responsed['role'] = None
						return responsed

				# edit the role
				try:
						r.__dict__.update(req['role'])
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				try:
						res = roledao.update(r)
						rcheck = roledao.getByName(r.rolename)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				if res and rcheck:
						responsed['response'] = "roleedited"
						responsed['responsen'] =  RESPONSE_OK
						responsed['description'] = "Role successfully edited"
						responsed['role'] = rcheck.dictexport()
						return responsed
				else:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Unknown Error"
						responsed['role'] = None
						return responsed

		def removerole(self, requser, req):
				if not requser.role.canManageRoles:
						responsed = {
										'response': "notallowed", 
										'responsen':  RESPONSE_NOTALLOWED,
										'description': "User role does not allow this action",
										'rolename': None
										}
						return responsed
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'rolename': None
								}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['rolename'] = None
						return responsed

				try:
						rolename = req['rolename']
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Check JSON Syntax [%s]" % str(e)
						responsed['rolename'] = None
						return responsed

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['rolename'] = rolename
						return responsed

				if r == None:
						responsed['response'] = "dontexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "Role not found" 
						responsed['rolename'] = rolename
						return responsed

				# remove the role
				try:
						res = roledao.removeByName(rolename)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['rolename'] = rolename
						return responsed

				if res:
						responsed['response'] = "roleremoved"
						responsed['responsen'] =  RESPONSE_OK
						responsed['description'] = "Role has been removed" 
						responsed['rolename'] = rolename
						return responsed

				else:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Unknown Error" 
						responsed['rolename'] = rolename
						return responsed

		def getrole(self, requser, req):
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'role': None
								}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				try:
						rolename = req['rolename']
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Check JSON Syntax [%s]" % str(e)
						responsed['role'] = None
						return responsed

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['role'] = None
						return responsed

				if not isinstance(r, Role):
						responsed['response'] = "dontexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "Role not found" 
						responsed['role'] = None
						return responsed
				
				responsed['response'] = "roleretrieved"
				responsed['responsen'] =  RESPONSE_OK
				responsed['description'] = "Role found" 
				responsed['role'] = r.dictexport()
				return responsed
		
		def listroles(self, requser, req):
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'listlength': 0,
								'rolelist': None
								}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['listlength'] = 0
						responsed['rolelist'] = None
						return responsed

				try:
						rlist = roledao.getAll()
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['listlength'] = 0
						responsed['rolelist'] = None
						return responsed

				rolelist = []
				for r in rlist:
						try:
								rolelist.append(r.dictexport())
						except Exception, e:
								responsed['response'] = "error"
								responsed['responsen'] =  RESPONSE_ERROR
								responsed['description'] = str(e) 
								responsed['listlength'] = 0
								responsed['rolelist'] = None
								return responsed

				responsed['response'] = "rolelistfollows"
				responsed['responsen'] =  RESPONSE_OK
				responsed['description'] = "Role list retrieved" 
				responsed['listlength'] = len(rlist)
				responsed['rolelist'] = rolelist
				return responsed

		def createuser(self, requser, req):
				if not requser.role.canManageUsers:
						responsed = {
										'response': "notallowed", 
										'responsen':  RESPONSE_NOTALLOWED,
										'description': "User role does not allow this action",
										'user': None
										}
						return responsed
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'user': None
								}
				try:
						u = User(req['user'])
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				try:
						ucheck = userdao.getByName(u.name)
				except RadioMateDAOException, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				if ucheck:
						responsed['response'] = "alreadyexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "User already exists"
						responsed['user'] = None
						return responsed

				try:
						roledao = RoleDAO(self.connectionmanager)
						rcheck = roledao.getByName(u.rolename)
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				if not rcheck:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Role %s does not exist" % u.rolename
						responsed['user'] = None
						return responsed

				try:
						res = userdao.insert(u)
						ucheck = userdao.getByName(u.name)
						if res and ucheck:
								responsed['response'] = "usercreated"
								responsed['responsen'] =  RESPONSE_OK
								responsed['description'] = "O.K."
								responsed['user'] = ucheck.dictexport()
								return responsed
				except RadioMateDAOException, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						return responsed
				except Exception, e:
						pass
				responsed['response'] = "error"
				responsed['responsen'] =  RESPONSE_ERROR
				responsed['description'] = str(e)
				responsed['user'] = None
				return responsed

		def edituser(self, requser, req):
				if not requser.role.canManageUsers:
						responsed = {
										'response': "notallowed", 
										'responsen':  RESPONSE_NOTALLOWED,
										'description': "User role does not allow this action",
										'user': None
										}
						return responsed
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'user': None
								}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				try:
						assert req['user']
						username = req['user']['name']
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Check JSON Syntax [%s]" % str(e)
						responsed['user'] = None
						return responsed

				try:
						u = userdao.getByName(username)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				if u == None:
						responsed['response'] = "dontexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "User %s not found" % username
						responsed['user'] = None
						return responsed

				# edit the user
				try:
						u.__dict__.update(req['user'])
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				try:
						res = userdao.update(u)
						ucheck = userdao.getByName(u.name)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				if res and ucheck:
						responsed['response'] = "useredited"
						responsed['responsen'] =  RESPONSE_OK
						responsed['description'] = "User successfully edited"
						responsed['user'] = ucheck.dictexport()
						return responsed
				else:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Unknown Error"
						responsed['user'] = None
						return responsed
		
		def removeuser(self, requser, req):
				if not requser.role.canManageUsers:
						responsed = {
										'response': "notallowed", 
										'responsen':  RESPONSE_NOTALLOWED,
										'description': "User role does not allow this action",
										'user': None
										}
						return responsed
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'name': None
								}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['name'] = None
						return responsed

				try:
						username = req['name']
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Check JSON Syntax [%s]" % str(e)
						responsed['name'] = None
						return responsed

				try:
						r = userdao.getByName(username)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['name'] = username
						return responsed

				if r == None:
						responsed['response'] = "dontexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "User not found" 
						responsed['name'] = username
						return responsed

				# remove the user
				try:
						res = userdao.removeByName(username)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['name'] = username
						return responsed

				if res:
						responsed['response'] = "userremoved"
						responsed['responsen'] =  RESPONSE_OK
						responsed['description'] = "User has been removed" 
						responsed['name'] = username
						return responsed

				else:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Unknown Error" 
						responsed['name'] = username
						return responsed

		def getuser(self, requser, req):
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'user': None
								}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				try:
						username = req['name']
				except Exception, e:
						responsed['response'] = "error"
						responsed['responsen'] =  RESPONSE_ERROR
						responsed['description'] = "Check JSON Syntax [%s]" % str(e)
						responsed['user'] = None
						return responsed

				try:
						u = userdao.getByName(username)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['user'] = None
						return responsed

				if not isinstance(u, User):
						responsed['response'] = "dontexists"
						responsed['responsen'] =  RESPONSE_EXISTANCE
						responsed['description'] = "User not found" 
						responsed['user'] = None
						return responsed
				
				responsed['response'] = "userretrieved"
				responsed['responsen'] =  RESPONSE_OK
				responsed['description'] = "User found" 
				responsed['user'] = u.dictexport()
				return responsed

		def listusers(self, requser, req):
				responsed = {
								'response': "error",
								'responsen':  RESPONSE_ERROR,
								'description': "Unknown Error",
								'listlength': 0,
								'userlist': None
								}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['listlength'] = 0
						responsed['userlist'] = None
						return responsed

				try:
						ulist = userdao.getAll()
				except Exception, e:
						responsed['response'] = "servererror"
						responsed['responsen'] =  RESPONSE_SERVERERROR
						responsed['description'] = str(e)
						responsed['listlength'] = 0
						responsed['userlist'] = None
						return responsed

				userlist = []
				for u in ulist:
						try:
								userlist.append(u.dictexport())
						except Exception, e:
								responsed['response'] = "error"
								responsed['responsen'] =  RESPONSE_ERROR
								responsed['description'] = str(e) 
								responsed['listlength'] = 0
								responsed['userlist'] = None
								return responsed

				responsed['response'] = "userlistfollows"
				responsed['responsen'] =  RESPONSE_OK
				responsed['description'] = "User list retrieved" 
				responsed['listlength'] = len(ulist)
				responsed['userlist'] = userlist
				return responsed

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

		

						
