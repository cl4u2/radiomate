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

# The JSON interface 

import json
import time
import config
from mate import *
from dao import *
from jukeslots.all import *
from mutagen.easyid3 import EasyID3
import os

RESPONSE_OK = 0
RESPONSE_NOTALLOWED = 101
RESPONSE_DONTEXISTS = 201
RESPONSE_ALREADYEXISTS = 202
RESPONSE_SERVERERROR = 301
RESPONSE_REQERROR = 401
RESPONSE_ERROR = 501
RESPONSE_NOTIMPLEMENTED = 601

ERRORDICT = {
				RESPONSE_OK: "ok",
				RESPONSE_NOTALLOWED: "notallowed",
				RESPONSE_ALREADYEXISTS: "alreadyexists",
				RESPONSE_DONTEXISTS: "dontexists",
				RESPONSE_SERVERERROR: "servererror",
				RESPONSE_REQERROR: "requesterror",
				RESPONSE_ERROR: "error",
				RESPONSE_NOTIMPLEMENTED: "notimplemented"
}


class RadioMateJSONError(Exception):
		"JSON API generic error"
		pass


class RadioMateJSONSyntaxError(Exception):
		"JSON syntax error"
		pass


class JsonRequest(dict):
		def __init__(self, jsonstring):
				dict.__init__(self)
				try:
						reqdict = json.loads(jsonstring)
						#TODO: validate the request
						self.update(reqdict)
				except Exception, e:
						raise RadioMateJSONSyntaxError(str(e))


class JsonResponse(dict):
		def __init__(self, responsen, description, responsedict = {}):
				dict.__init__(self)
				try:
						dict.__setitem__(self, 'responsen', responsen)
						dict.__setitem__(self, 'response', ERRORDICT[responsen])
						dict.__setitem__(self, 'description', description)
						dict.__setitem__(self, 'warning', None)
						self.update(responsedict)
				except Exception, e:
						raise RadioMateJSONError(str(e))

		def dumps(self):
				return json.dumps(self, skipkeys=True)
		

class JSONProcessor(object):
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
						req = JsonRequest(request)
				except Exception, e:
						response = JsonResponse(RESPONSE_REQERROR, "Incorrect JSON Request [%s]" % str(e))
						return response.dumps()
				
				if not req.has_key('request') or (req['request'] == ''):
						response = JsonResponse(RESPONSE_REQERROR, "Incorrect JSON Request [%s]" % str(e))
						return response.dumps()

				# if required get a new session ID from username and password
				if req.has_key('request') and (req['request'] == 'login'):
						try:
								response = self.login(req)
						except Exception, e:
								response = JsonResponse(RESPONSE_NOTALLOWED, "Not Allowed (Login) [%s]" % str(e))
						return response.dumps()

				# validate username and session ID
				try:
						sessiondao = SessionDAO(self.connectionmanager)
						username = req['username']
						sessionid = req['sessionid']
						requser = sessiondao.checkSessionID(username, sessionid)
						if not requser: 
								raise RadioMateJSONError("Invalid session ID. Expired?")
				except Exception, e:
						response = JsonResponse(RESPONSE_NOTALLOWED, "Not Allowed (Session) [%s]" % str(e))
						return response.dumps()
				
				# small python magic to call the method that has the same name of the request
				if req.has_key('request') and (req['request'] in self.__class__.__dict__):
						response = self.__class__.__dict__[req['request']](self, requser, req)
				else:
						response = JsonResponse(RESPONSE_REQERROR, "Incorrect JSON Request")

				return response.dumps()
		
		def login(self, req):
				rd = {'requested': "login", 'username': None, 'sessionid': None}
				try:
						sessiondao = SessionDAO(self.connectionmanager)
						username = req['username']
						rd['username'] = username
						password = req['password']
						sessionid = sessiondao.newSession(username, password)
						if not sessionid:
								return JsonResponse(RESPONSE_NOTALLOWED, "Invalid username and/or password", rd)
						else:
								rd['sessionid'] = sessionid
								return JsonResponse(RESPONSE_OK, "New Session", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
		
		def logout(self, requser, req):
				rd = {'requested': "logout"}
				try:
						sessiondao = SessionDAO(self.connectionmanager)
						username = req['username']
						rd['username'] = username
						sessionid = req['sessionid']
						if sessiondao.logout(username, sessionid):
								return JsonResponse(RESPONSE_OK, "Logged out", rd)
						else:
								return JsonResponse(RESPONSE_NOTALLOWED, "Invalid username and/or session id", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

		def createrole(self, requser, req):
				rd = {'requested': "createrole", 'role': None}
				if not requser.role.canManageRoles:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						r = Role(req['role'])
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						rcheck = roledao.getByName(r.rolename)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if rcheck:
						return JsonResponse(RESPONSE_ALREADYEXISTS, "Role already exists", rd)

				try:
						res = roledao.insert(r)
						rcheck = roledao.getByName(r.rolename)
						if res and rcheck:
								rd['role'] = rcheck.dictexport()
								return JsonResponse(RESPONSE_OK, "Role created", rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except Exception, e:
						pass
				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def editrole(self, requser, req):
				rd = {'requested': "editrole", 'role': None}
				if not requser.role.canManageRoles:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						assert req['role']
						rolename = req['role']['rolename']
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not r:
						return JsonResponse(RESPONSE_DONTEXISTS, "Role %s not found" % rolename, rd)

				# edit the role
				try:
						r.dictupdate(req['role'])
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				try:
						res = roledao.update(r)
						rcheck = roledao.getByName(r.rolename)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res and rcheck:
						rd['role'] = rcheck.dictexport()
						return JsonResponse(RESPONSE_OK, "Role successfully edited", rd)
				else:
						return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def removerole(self, requser, req):
				rd = {'requested': "removerole", 'rolename': None}
				if not requser.role.canManageRoles:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						rolename = req['rolename']
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not r:
						return JsonResponse(RESPONSE_DONTEXISTS, "Role %s not found" % rolename, rd)

				# remove the role
				try:
						res = roledao.removeByName(rolename)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res:
						rd['rolename'] = rolename
						return JsonResponse(RESPONSE_OK, "Role has been removed", rd)

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def getrole(self, requser, req):
				rd = {'requested': "getrole", 'role': None}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						rolename = req['rolename']
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						r = roledao.getByName(rolename)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not isinstance(r, Role):
						return JsonResponse(RESPONSE_DONTEXISTS, "Role %s not found" % rolename, rd)
				
				rd['role'] = r.dictexport()
				return JsonResponse(RESPONSE_OK, "Role found", rd)
		
		def listroles(self, requser, req):
				rd = {'requested': "listroles", 'listlength':0, 'rolelist': []}
				try:
						roledao = RoleDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				try:
						rlist = roledao.getAll()
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				rolelist = []
				for r in rlist:
						try:
								rolelist.append(r.dictexport())
						except Exception, e:
								return JsonResponse(RESPONSE_ERROR, str(e), rd)

				rd['listlength'] = len(rlist)
				rd['rolelist'] = rolelist
				return JsonResponse(RESPONSE_OK, "Role list retrieved", rd)

		def createuser(self, requser, req):
				rd = {'requested': "createuser", 'user': None}
				if not requser.role.canManageUsers:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)
				try:
						u = User(req['user'])
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						ucheck = userdao.getByName(u.name)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if ucheck:
						return JsonResponse(RESPONSE_ALREADYEXISTS, "User already exists", rd)

				try:
						roledao = RoleDAO(self.connectionmanager)
						rcheck = roledao.getByName(u.rolename)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if not rcheck:
						return JsonResponse(RESPONSE_ERROR, "Role %s does not exist" % u.rolename, rd)

				try:
						res = userdao.insert(u)
						ucheck = userdao.getByName(u.name)
						if res and ucheck:
								rd['user'] = ucheck.dictexport()
								return JsonResponse(RESPONSE_OK, "User successfully created", rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except Exception, e:
						raise
						#return JsonResponse(RESPONSE_ERROR, str(e), rd)
				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def edituser(self, requser, req):
				rd = {'requested': "edituser", 'user': None}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						assert req['user']
						username = req['user']['name']
				except Exception, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax [%s]" % str(e), rd)
				
				# only the user herself and the role manager can do this
				if requser.name != username and not requser.role.canManageUsers:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						u = userdao.getByName(username)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not u:
						return JsonResponse(RESPONSE_DONTEXISTS, "User %s not found" % username, rd)

				# edit the user
				try:
						u.dictupdate(req['user'])
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				try:
						res = userdao.update(u)
						ucheck = userdao.getByName(u.name)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res and ucheck:
						rd['user'] = ucheck.dictexport()
						return JsonResponse(RESPONSE_OK, "User successfully edited", rd)
				else:
						return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)
		
		def removeuser(self, requser, req):
				rd = {'requested': "removeuser", 'name': None}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						username = req['name']
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, "Check JSON Syntax [%s]" % str(e), rd)

				# only the user herself and the role manager can do this
				if requser.name != username and not requser.role.canManageUsers:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						u = userdao.getByName(username)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not u:
						return JsonResponse(RESPONSE_DONTEXISTS, "User %s not found" % username, rd)

				# remove the user
				try:
						res = userdao.removeByName(username)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res:
						rd['name'] = username
						return JsonResponse(RESPONSE_OK, "User has been removed", rd)

				else:
						return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def getuser(self, requser, req):
				rd = {'requested': "getuser", 'user': None}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						username = req['name']
				except Exception, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						u = userdao.getByName(username)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if not isinstance(u, User):
						return JsonResponse(RESPONSE_DONTEXISTS, "User %s not found" % username, rd)
				
				rd['user'] = u.dictexport()
				return JsonResponse(RESPONSE_OK, "User found", rd)

		def listusers(self, requser, req):
				rd = {'requested': "listusers", 'listlength': 0, 'userlist': []}
				try:
						userdao = UserDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						ulist = userdao.getAll()
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				userlist = []
				for u in ulist:
						try:
								userlist.append(u.dictexport())
						except Exception, e:
								return JsonResponse(RESPONSE_ERROR, str(e), rd)

				rd['listlength'] = len(ulist)
				rd['userlist'] = userlist
				return JsonResponse(RESPONSE_OK, "User list retrieved", rd)

		def registerfile(self, requser, req):
				rd = {'requested': "registerfile", 'mediafile': None}
				if not requser.role.canRegisterFiles:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				try:
						m = MediaFile(req['mediafile'])
						m.user = requser.name
				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax. Mediafile missing?", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				try:
						mediafiledao = MediaFileDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				# check if file has already been registered
				try:
						mcheck = mediafiledao.getByPath(m.path)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if len(mcheck) > 0:
						rd['warning'] = "File at this path already registered"

				try:
						id = mediafiledao.insert(m)
						mcheck = mediafiledao.getById(id)
						if id and mcheck:
								rd['mediafile'] = mcheck.dictexport()
								return JsonResponse(RESPONSE_OK, "MediaFile successfully registered", rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except Exception, e:
						pass
				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def scanfile(self, requser, req):
				"Scan a file for ID3 tags and return them. No registration is performed."
				rd = {'requested': "scanfile", 'mediafile': None}
				try:
						m = MediaFile()
						mpath = req['path']
						m.path = mpath
						m.user = requser.name
						m.title = os.path.basename(mpath).split('+')[-1]
						rd['mediafile'] = m.dictexport()
						mfid3 = EasyID3(mpath)
				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax. Mediafile missing?", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				try:
						m.author = str(mfid3['artist'][0])
				except KeyError, e:
						pass

				try:
						m.album = str(mfid3['album'][0])
				except KeyError, e:
						pass
				
				try:
						m.year = int(mfid3['date'][0])
				except KeyError, e:
						pass
				except ValueError, e:
						pass
				
				try:
						m.title = str(mfid3['title'][0])
				except KeyError, e:
						pass

				try:
						m.genre = str(mfid3['genre'][0])
				except KeyError, e:
						pass

				try:
						m.license = str(mfid3['copyright'][0])
				except KeyError, e:
						pass

				rd['mediafile'] = m.dictexport()
				return JsonResponse(RESPONSE_OK, "MediaFile Scanned", rd)
		
		def getfile(self, requser, req):
				rd = {'requested': "getfile", 'mediafile': None}
				try:
						mediafileid = int(req['mediafileid'])
				except Exception, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						mediafiledao = MediaFileDAO(self.connectionmanager)
						m = mediafiledao.getById(mediafileid)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				
				if m:
						rd['mediafile'] = m.dictexport()
						return JsonResponse(RESPONSE_OK, "MediaFile Found", rd)
				else:
						return JsonResponse(RESPONSE_DONTEXISTS, "MediaFile not Found", rd)

		def searchfiles(self, requser, req):
				rd = {'requested': "searchfiles", 'listlength': 0, 'mediafilelist': []}
				try:
						m = MediaFile(req['mediafile'])
				except Exception, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						mediafiledao = MediaFileDAO(self.connectionmanager)
						mlist = mediafiledao.search(m)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				
				mediafilelist = []
				for m in mlist:
						try:
								mediafilelist.append(m.dictexport())
						except Exception, e:
								return JsonResponse(RESPONSE_ERROR, str(e), rd)

				rd['listlength'] = len(mediafilelist)
				rd['mediafilelist'] = mediafilelist
				return JsonResponse(RESPONSE_OK, "List Follows", rd)
		
		def fullsearchfiles(self, requser, req):
				rd = {'requested': "fullsearchfiles", 'listlength': 0, 'mediafilelist': []}
				try:
						searchterm = req['q'].strip()
						rd['q'] = searchterm
				except Exception, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						mediafiledao = MediaFileDAO(self.connectionmanager)
						mlist = mediafiledao.searchAllFields(searchterm)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				
				mediafilelist = []
				for m in mlist:
						try:
								mediafilelist.append(m.dictexport())
						except Exception, e:
								return JsonResponse(RESPONSE_ERROR, str(e), rd)

				rd['listlength'] = len(mediafilelist)
				rd['mediafilelist'] = mediafilelist
				return JsonResponse(RESPONSE_OK, "List Follows", rd)

		def editfile(self, requser, req):
				"""An user can edit her own files or, if she has the 
				canManageRegisteredFiles permission, can manage every media file"""

				rd = {'requested': "editfile", 'mediafile': None}
				try:
						mediafiledao = MediaFileDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						m = mediafiledao.getById(int(req['mediafile']['id']))
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check mediafile id in JSON syntax", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if requser.name != m.user and not requser.role.canManageRegisteredFiles:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				if not m:
						return JsonResponse(RESPONSE_DONTEXISTS, "Media file %d not found" % m.id, rd)

				# edit the mediafile
				try:
						m.dictupdate(req['mediafile'])
						id = mediafiledao.update(m)
						mcheck = mediafiledao.getById(id)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if id and mcheck:
						rd['mediafile'] = mcheck.dictexport()
						return JsonResponse(RESPONSE_OK, "Media File successfully edited", rd)

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)
		
		def unregisterfile(self, requser, req):
				"""An user can unregister her own files or, if she has the 
				canManageRegisteredFiles permission, can unregister every media file"""

				rd = {'requested': "unregisterfile", 'mediafileid': None}
				try:
						mediafiledao = MediaFileDAO(self.connectionmanager)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				try:
						mediafileid = int(req['mediafileid'])
						m = mediafiledao.getById(mediafileid)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check mediafileid in JSON syntax", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if requser.name != m.user and not requser.role.canManageRegisteredFiles:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				if not m:
						return JsonResponse(RESPONSE_DONTEXISTS, "Media file %d not found" % m.id, rd)

				# deregister the mediafile
				try:
						res = mediafiledao.removeById(mediafileid)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)

				if res:
						rd['mediafileid'] = mediafileid
						return JsonResponse(RESPONSE_OK, "Media File successfully unregistered", rd)

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def createplaylist(self, requser, req):
				rd = {'requested': "createplaylist", 'playlist': None}
				try:
						del req['playlist']['id']
						p = PlayList(req['playlist'])
						p.creator = requser.name
						p.addOwner(requser.name)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				try:
						playlistdao = PlayListDAO(self.connectionmanager)
						id = playlistdao.insert(p)
						pcheck = playlistdao.getById(id)
						if id and pcheck:
								rd['playlist'] = pcheck.dictexport()
								return JsonResponse(RESPONSE_OK, "Playlist successfully created", rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def editplaylist(self, requser, req):
				rd = {'requested': "editplaylist", 'playlist': None}
				try:
						playlistdao = PlayListDAO(self.connectionmanager)
						p = playlistdao.getById(int(req['playlist']['id']))
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if not p:
						return JsonResponse(RESPONSE_DONTEXISTS, "Playlist not found", rd)

				if requser.name != p.creator and (not requser.name in p.owners) and not requser.role.canManageAllPlaylists:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				# edit the playlist
				try:
						p.dictupdate(req['playlist'])
						p.addOwner(requser.name)
						id = playlistdao.update(p)
						pcheck = playlistdao.getById(id)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if id and pcheck:
						rd['playlist'] = pcheck.dictexport()
						return JsonResponse(RESPONSE_OK, "Playlist successfully edited", rd)

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)
		
		def removeplaylist(self, requser, req):
				rd = {'requested': "removeplaylist", 'playlistid': None}
				try:
						playlistdao = PlayListDAO(self.connectionmanager)
						playlistid = int(req['playlistid'])
						p = playlistdao.getById(playlistid)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if not p:
						return JsonResponse(RESPONSE_DONTEXISTS, "Playlist not found", rd)

				if requser.name != p.creator and (not requser.name in p.owners) and not requser.role.canManageAllPlaylists:
						return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

				# remove the playlist
				try:
						res = playlistdao.removeById(playlistid)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

				if res:
						rd['playlist'] = playlistid
						return JsonResponse(RESPONSE_OK, "Playlist successfully removed", rd)

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def addfilestoplaylist(self, requser, req):
				rd = {'requested': "addfilestoplaylist", 'numberoffilesadded': 0, 'playlist': None}
				try:
						playlistdao = PlayListDAO(self.connectionmanager)
						mediafiledao = MediaFileDAO(self.connectionmanager)
						playlistid = int(req['playlistid'])
						mediafileidlist = []
						if len(req['mediafileidlist']) == 0:
								JsonResponse(RESPONSE_OK, "Ok, but no files added to the playlist", rd)
						else:
								for ids in req['mediafileidlist']:
										mediafileidlist.append(int(ids))
						p = playlistdao.getById(playlistid)

						if requser.name != p.creator and (not requser.name in p.owners) and not requser.role.canManageAllPlaylists:
								return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

						n = 0
						for id in mediafileidlist:
								mf = mediafiledao.getById(id)
								p.addMediaFile(mf)
								n+=1
						id = playlistdao.update(p)
						pcheck = playlistdao.getById(id)
						if id and pcheck:
								rd['numberoffilesadded'] = n
								rd['playlist'] = pcheck.dictexport()
								return JsonResponse(RESPONSE_OK, "Playlist successfully edited", rd)
						return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

		def removefilesfromplaylist(self, requser, req):
				rd = {'requested': "removefilesfromplaylist", 'numberoffilesremoved': 0, 'playlist': None}
				try:
						playlistdao = PlayListDAO(self.connectionmanager)
						playlistid = int(req['playlistid'])
						if len(req['mediafilepositionlist']) == 0:
								JsonResponse(RESPONSE_OK, "Ok, but no files removed from the playlist", rd)
						else:
								mediafileposlist = []
								for pos in req['mediafilepositionlist']:
										mediafileposlist.append(int(pos))
						p = playlistdao.getById(playlistid)
						
						if requser.name != p.creator and (not requser.name in p.owners) and not requser.role.canManageAllPlaylists:
								return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

						n = 0
						mediafileposlist.sort()
						mediafileposlist.reverse()
						for pos in mediafileposlist:
								p.removeMediaFile(pos)
								n+=1
						id = playlistdao.update(p)
						pcheck = playlistdao.getById(id)
						if id and pcheck:
								rd['numberoffilesremoved'] = n
								rd['playlist'] = pcheck.dictexport()
								return JsonResponse(RESPONSE_OK, "Playlist successfully edited", rd)
						return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

		def movefilesinplaylist(self, requser, req):
				rd = {'requested': "movefilesinplaylist", 'playlist': None}
				try:
						playlistdao = PlayListDAO(self.connectionmanager)

						playlistid = int(req['playlistid'])
						oldmediafileposition = int(req['oldmediafileposition'])
						newmediafileposition = int(req['newmediafileposition'])

						p = playlistdao.getById(playlistid)
						
						if requser.name != p.creator and (not requser.name in p.owners) and not requser.role.canManageAllPlaylists:
								return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

						mflist = p.mediafilelist[:]
						oldmf = mflist[oldmediafileposition]
						listlen = len(mflist)

						if newmediafileposition > len(mflist):
								newmediafileposition = len(mflist)

						if newmediafileposition < 0:
								newmediafileposition = 0

						if oldmediafileposition == newmediafileposition:
								rd['warning'] = "No change made"
						else:
								if newmediafileposition >= len(mflist):
										mflist.append(oldmf)
								elif newmediafileposition <= 0:
										mflist.insert(0, oldmf)
								else:
										if newmediafileposition > oldmediafileposition:
												mflist.insert(newmediafileposition + 1, oldmf)
										else:
												mflist.insert(newmediafileposition, oldmf)

								if newmediafileposition > oldmediafileposition:
										del mflist[oldmediafileposition]
								else:
										del mflist[oldmediafileposition + 1]
								assert len(mflist) == listlen

								p.mediafilelist = mflist
								playlistdao.update(p)
						rd['playlist'] = p.dictexport()
						return JsonResponse(RESPONSE_OK, "Playlist successfully edited", rd)

				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

		def listuserplaylists(self, requser, req):
				rd = {'requested': "listuserplaylists", 'listlength': 0, 'playlistlist': []}
				try:
						if req.has_key('user'):
								userreq = req['user']
						else:
								userreq = req['username']

						if requser.name == userreq or requser.role.canManageAllPlaylists:
								getprivate = True
						else:
								getprivate = False

						playlistdao = PlayListDAO(self.connectionmanager)
						plist = playlistdao.getByUser(userreq, getprivate)

						playlistlist = [p.dictexport() for p in plist]
						rd['listlength'] = len(playlistlist)
						rd['playlistlist'] = playlistlist
						return JsonResponse(RESPONSE_OK, "List Follows", rd)
				
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except NameError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON syntax [%s]" % str(e), rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
		
		def getplaylist(self, requser, req):
				rd = {'requested': "getplaylist", 'playlist': None}
				try:
						playlistid = int(req['playlistid'])
				except Exception, e:
						return JsonResponse(RESPONSE_REQERROR, "Check JSON Syntax [%s]" % str(e), rd)

				try:
						playlistdao = PlayListDAO(self.connectionmanager)
						p = playlistdao.getById(playlistid)
				except Exception, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				
				if p:
						rd['playlist'] = p.dictexport()
						return JsonResponse(RESPONSE_OK, "Playlist Found", rd)
				else:
						return JsonResponse(RESPONSE_DONTEXISTS, "Playlist not Found", rd)
				
		def reservetimeslot(self, requser, req):
				rd = {'requested': "reservetimeslot", 'timeslot': None}
				try:
						t = TimeSlot(req['timeslot'])
						t.creator = requser.name
				except Exception, e:
						return JsonResponse(RESPONSE_REQERROR, str(e), rd)

				if requser.role.fixedSlotTimes and not t.duration in requser.role.fixedSlotTimesListList():
						return JsonResponse(RESPONSE_NOTALLOWED, 
										"User role does not allow this action. Fixed slot times: %s." % \
										requser.role.fixedSlotTimesList, rd)
						
				try:
						# check the slot type
						jukeslotclass = JUKESLOTTYPEDICT[t.slottype]
						tj = jukeslotclass(timeslot=t, mainpassword="")
						tj.liquidsoapcode()
				except:
						raise
						return JsonResponse(RESPONSE_REQERROR, "Slot type not supported or wrong slot parameters")

				try:
						timeslotdao = TimeSlotDAO(self.connectionmanager)
						if t.id > 0:
								if timeslotdao.getById(t.id):
										return JsonResponse(RESPONSE_ERROR, "Timeslot conflict. Id already exists.", rd)
						id = timeslotdao.insert(t)
						tcheck = timeslotdao.getById(id)
						if id and tcheck:
								rd['timeslot'] = tcheck.dictexport()
								return JsonResponse(RESPONSE_OK, "Timeslot successfully reserved", rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except RadioMateBadTimeSlotException, e:
						return JsonResponse(RESPONSE_ERROR, "Timeslot conflict. Cannot reserve.", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except:
						pass

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)
		
		def unreservetimeslot(self, requser, req):
				rd = {'requested': "unreservetimeslot", 'timeslotid': None}
				try:
						id = req['timeslotid']
						timeslotdao = TimeSlotDAO(self.connectionmanager)
						t = timeslotdao.getById(id)
						if t.creator != requser.name and not requser.role.canManageTimetable:
								return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

						res = timeslotdao.removeById(id)
						if res:
								rd['timeslotid'] = id
								return JsonResponse(RESPONSE_OK, "Timeslot successfully unreserved", rd)
						else:
								return JsonResponse(RESPONSE_SERVERERROR, "Something went wrong. Timeslot NOT unreserved", rd)
				except KeyError:
						return JsonResponse(RESPONSE_REQERROR, str(e), rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except RadioMateBadTimeSlotException, e:
						return JsonResponse(RESPONSE_ERROR, "Timeslot conflict. Cannot reserve.", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except: 
						return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def edittimeslot(self, requser, req):
				rd = {'requested': "edittimeslot", 'timeslot': None}
				try:
						id = int(req['timeslot']['id'])

						timeslotdao = TimeSlotDAO(self.connectionmanager)
						t = timeslotdao.getById(id)
						
						if t.creator != requser.name and not requser.role.canManageTimetable:
								return JsonResponse(RESPONSE_NOTALLOWED, "User role does not allow this action", rd)

						t.dictupdate(req['timeslot'])

						if t.canceled and not requser.role.canManageTimetable:
								return JsonResponse(RESPONSE_NOTALLOWED, "User cannot cancel a show", rd)

						if requser.role.changeTimeBeforeTransmission > 0:
								seconds2transmission = t.getBeginningTimestamp() - time.time()
								if seconds2transmission <= requser.role.changeTimeBeforeTransmission*60:
										return JsonResponse(RESPONSE_NOTALLOWED, 
														"Changing time %d seconds before transmission is not allowed" % \
																		seconds2transmission, rd)

						try:
								# check the slot type
								jukeslotclass = JUKESLOTTYPEDICT[t.slottype]
								tj = jukeslotclass(timeslot=t, mainpassword="")
								tj.liquidsoapcode()
						except:
								return JsonResponse(RESPONSE_REQERROR, "Slot type not supported or wrong slot parameters")

						newid = timeslotdao.update(t)
						if newid != id:
								return JsonResponse(RESPONSE_SERVERERROR, "Something wrong: %d -> %d" % (id, newid), rd)
						tcheck = timeslotdao.getById(id)
						if tcheck:
								rd['timeslot'] = tcheck.dictexport()
								return JsonResponse(RESPONSE_OK, "Timeslot successfully edited", rd)
				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, str(e), rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except RadioMateBadTimeSlotException, e:
						return JsonResponse(RESPONSE_ERROR, "Timeslot conflict. Cannot reserve.", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except:
						pass

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def listtimeslots(self, requser, req):
				rd = {'requested': "listtimeslots", 'listlength': 0, 'timeslotlist': []}
				try:
						timeslotdao = TimeSlotDAO(self.connectionmanager)
						if req['timeslot'].has_key('id'):
								t = timeslotdao.getById(req['timeslot']['id'])
								rd['listlength'] = 1
								rd['timeslotlist'] = [t.dictexport()]
								return JsonResponse(RESPONSE_OK, "One timeslot retrieved, by id", rd)
						elif req['timeslot'].has_key('from') and req['timeslot'].has_key('to'):
								dummyts = TimeSlot() #used for format conversion

								dummyts.beginningtime = req['timeslot']['from']
								fromdate = dummyts.getBeginningDatetime()

								dummyts.beginningtime = req['timeslot']['to']
								todate = dummyts.getBeginningDatetime()

								tlist = timeslotdao.getFromTo(fromdate, todate)
								timeslotlist = [t.dictexport() for t in tlist]
								rd['listlength'] = len(timeslotlist)
								rd['timeslotlist'] = timeslotlist
								return JsonResponse(RESPONSE_OK, "List Follows, retrieved by time", rd)
						else:
								t = TimeSlot()
								t.dictupdate(req['timeslot'])
								tlist = timeslotdao.search(t)
								timeslotlist = [t.dictexport() for t in tlist]
								rd['listlength'] = len(timeslotlist)
								rd['timeslotlist'] = timeslotlist
								return JsonResponse(RESPONSE_OK, "List Follows, by searching", rd)

				except KeyError, e:
						return JsonResponse(RESPONSE_REQERROR, str(e), rd)
				except RadioMateDAOException, e:
						return JsonResponse(RESPONSE_SERVERERROR, str(e), rd)
				except RadioMateBadTimeSlotException, e:
						return JsonResponse(RESPONSE_ERROR, "Timeslot conflict. Cannot reserve.", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)
				except:
						pass

				return JsonResponse(RESPONSE_ERROR, "Unknown Error", rd)

		def createtestslot(self, requser, req):
				# TODO implement createtestslot
				rd = {'requested': "createtestslot"}
				return JsonResponse(RESPONSE_NOTIMPLEMENTED, "Not yet implemented", rd)

		def listnetcasts(self, requser, req):
				#TODO implement listnetcasts
				rd = {'requested': "listnetcasts"}
				return JsonResponse(RESPONSE_NOTIMPLEMENTED, "Not yet implemented", rd)

		def listslottypes(self, requser, req):
				"return the available timeslot/JukeSlot types"
				rd = {'requested': "listslottypes", 'listlength': 0, 'slottypeslist': []}
				try:
						rd['slottypeslist'] = JUKESLOTTYPEDICT.keys()
						rd['listlength'] = len(rd['slottypeslist'])
						return JsonResponse(RESPONSE_OK, "Available slot type list follows", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

		def getslotreqparameters(self, requser, req):
				"return the requested parameters for a timeslot/JukeSlot type"
				rd = {'requested': "getslotreqparameters", 'slottype': "", 'listlength': 0, 'parameters': []}
				try:
						slottypename = req['slottype']
						rd['slottype'] = slottypename
						rd['parameters'] = JUKESLOTREQUIREDPARAMS[slottypename]
						rd['listlength'] = len(rd['parameters'])
						return JsonResponse(RESPONSE_OK, "Available slot type list follows", rd)
				except Exception, e:
						return JsonResponse(RESPONSE_ERROR, str(e), rd)

