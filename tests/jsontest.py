# vim:fileencoding=utf-8:nomodified
# $Id$

from radiomate import jsonif
import json


def processandcheck(jsonrequest, check = True, ret = None):
		print jsonrequest
		r = jp.process(jsonrequest)
		print r
		rd = json.loads(r)
		if check and int(rd['responsen']) != 0:
				print rd['responsen']
				raise SystemExit("Test Failed")
		if ret:
				return rd[ret]

def logintest():
		jsonrequest = """
		{
			"request": "login",
			"username": "foobar",
			"password": "secret"
		}
		""" 
		return processandcheck(jsonrequest, ret='sessionid')


def roletest(sessionid):
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"sessionid": "%s",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": false,
				"canRegisterFiles": false,
				"canManageRegisteredFiles": false,
				"canManageTimetable": false,
				"fixedSlotTimes": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": -1,
				"canCreateTestSlot": false
			}
		}
		""" % sessionid
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "getrole",
			"username": "foobar",
			"sessionid": "%s",
			"rolename": "testrole"
		}
		""" % sessionid
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "listroles",
			"username": "foobar",
			"sessionid": "%s"
		}
		""" % sessionid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"sessionid": "%s",
			"rolename": "testroule"
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"sessionid": "%s",
			"rolename": "testrole"
		}
		""" % sessionid
		processandcheck(jsonrequest)

def usertest(sessionid):
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"sessionid": "%s",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": false,
				"canRegisterFiles": false,
				"canManageRegisteredFiles": false,
				"canManageTimetable": false,
				"fixedSlotTimes": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": -1,
				"canCreateTestSlot": false
			}
		}
		""" % sessionid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"sessionid": "%s",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"email": "test@test.net",
				"rolename": "testrole"
			}
		}
		""" % sessionid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "getuser",
			"username": "foobar",
			"sessionid": "%s",
			"name": "testuser"
		}
		""" % sessionid
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "listusers",
			"username": "foobar",
			"sessionid": "%s"
		}
		""" % sessionid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"sessionid": "%s",
			"name": "testusser"
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"sessionid": "%s",
			"name": "testuser"
		}
		""" % sessionid
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"sessionid": "%s",
			"rolename": "testrole"
		}
		""" % sessionid
		processandcheck(jsonrequest)

def mediafiletest(sessionid):
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"sessionid": "%s",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": false,
				"canRegisterFiles": true,
				"canManageRegisteredFiles": true,
				"canManageTimetable": false,
				"fixedSlotTimes": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": -1,
				"canCreateTestSlot": false
			}
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"sessionid": "%s",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "foobar",
			"sessionid": "%s",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"path": "ugly/test.mp3",
				"title": "Just A Test Track",
				"author": "Me",
				"album": "My Album",
				"genre": "tests",
				"year": 2010,
				"comment": "Awful track",
				"license": "public domain",
				"tags": "me, justatest"
			}
		}
		""" % sessionid
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		print mediafile
		id = mediafile['id']
		
		jsonrequest = """
		{
			"request": "getfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafileid": %d
		}
		""" % (sessionid, id)
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		print mediafile
		
		jsonrequest = """
		{
			"request": "searchfiles",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"path": "ugly/",
				"year": 2010
			}
		}
		""" % sessionid
		mediafilelist = processandcheck(jsonrequest, ret='mediafilelist')
		print mediafilelist
		
		jsonrequest = """
		{
			"request": "searchfiles",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"user": "testuser"
			}
		}
		""" % sessionid
		mediafilelist = processandcheck(jsonrequest, ret='mediafilelist')
		print mediafilelist
		
		jsonrequest = """
		{
			"request": "editfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"id": %d,
				"title": "It Was Just A Test Track"
			}
		}
		""" % (sessionid, id)
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		print mediafile
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafileid": %d
		}
		""" % (sessionid, id)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"sessionid": "%s",
			"name": "testuser"
		}
		""" % sessionid
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"sessionid": "%s",
			"rolename": "testrole"
		}
		""" % sessionid
		processandcheck(jsonrequest)

def playlisttest(sessionid):
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"sessionid": "%s",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": true,
				"canRegisterFiles": true,
				"canManageRegisteredFiles": true,
				"canManageTimetable": false,
				"fixedSlotTimes": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": -1,
				"canCreateTestSlot": false
			}
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"sessionid": "%s",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"path": "ugly/test.mp3",
				"title": "Just A Test Track",
				"author": "Me",
				"album": "My Album",
				"genre": "tests",
				"year": 2010,
				"comment": "Awful track",
				"license": "public domain",
				"tags": "me, justatest"
			}
		}
		""" % sessionid
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id1 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"path": "bad/test.mp3",
				"title": "Just Another Test Track",
				"author": "Myself",
				"album": "My Own Album",
				"genre": "tests",
				"year": 2010,
				"comment": "Just a track",
				"license": "public domain",
				"tags": "me, justatest"
			}
		}
		""" % sessionid
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id2 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "createplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlist": {
					"title": "Test Playlist",
					"description": "Some Test Tracks",
					"comment": "Bad Music",
					"tags": "me, justatest",
					"private": true,
					"random": false,
					"viewers": [ "foobar" ],
					"owners": [ "testuser", "foobar" ]
			}
		}
		""" % sessionid
		playlist = processandcheck(jsonrequest, ret='playlist')
		pid = playlist['id']
		
		jsonrequest = """
		{
			"request": "addfilestoplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlistid": %d,
			"mediafileidlist": [ %d, %d ]
		}
		""" % (sessionid, pid, id1, id2)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "movefilesinplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlistid": %d,
			"oldmediafileposition": %d, 
			"newmediafileposition": %d 
		}
		""" % (sessionid, pid, 1, 0)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removefilesfromplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlistid": %d,
			"mediafilepositionlist": [ 0 ]
		}
		""" % (sessionid, pid)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "editplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlist": {
					"id": %d,
					"title": "Modified Playlist"
			}
		}
		""" % (sessionid, pid)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listuserplaylists",
			"username": "foobar",
			"sessionid": "%s",
			"user": "admin"
		}
		""" % sessionid
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlistid": %d
		}
		""" % (sessionid, pid)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafileid": %d
		}
		""" % (sessionid, id1)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafileid": %d
		}
		""" % (sessionid, id2)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"sessionid": "%s",
			"name": "testuser"
		}
		""" % sessionid
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"sessionid": "%s",
			"rolename": "testrole"
		}
		""" % sessionid
		processandcheck(jsonrequest)

def timeslottest(sessionid):
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"sessionid": "%s",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": true,
				"canRegisterFiles": true,
				"canManageRegisteredFiles": true,
				"canManageTimetable": false,
				"fixedSlotTimes": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": -1,
				"canCreateTestSlot": false
			}
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"sessionid": "%s",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		""" % sessionid
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"path": "ugly/test.mp3",
				"title": "Just A Test Track",
				"author": "Me",
				"album": "My Album",
				"genre": "tests",
				"year": 2010,
				"comment": "Awful track",
				"license": "public domain",
				"tags": "me, justatest"
			}
		}
		""" % sessionid
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id1 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafile": {
				"path": "bad/test.mp3",
				"title": "Just Another Test Track",
				"author": "Myself",
				"album": "My Own Album",
				"genre": "tests",
				"year": 2010,
				"comment": "Just a track",
				"license": "public domain",
				"tags": "me, justatest"
			}
		}
		""" % sessionid
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id2 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "createplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlist": {
					"title": "Test Playlist",
					"description": "Some Test Tracks",
					"comment": "Bad Music",
					"tags": "me, justatest",
					"private": true,
					"random": false,
					"viewers": [ "foobar" ],
					"owners": [ "testuser", "foobar" ]
			}
		}
		""" % sessionid
		playlist = processandcheck(jsonrequest, ret='playlist')
		pid = playlist['id']
		
		jsonrequest = """
		{
			"request": "addfilestoplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlistid": %d,
			"mediafileidlist": [ %d, %d ]
		}
		""" % (sessionid, pid, id1, id2)
		playlist = processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "listslottypes",
			"username": "foobar",
			"sessionid": "%s"
		}
		""" % sessionid
		slottypelist = processandcheck(jsonrequest, ret='slottypeslist')
		print "slottypelist = " , slottypelist

		jsonrequest = """
		{
			"request": "reservetimeslot",
			"username": "foobar",
			"sessionid": "%s",
			"timeslot" : {
					"title": "Test Timeslot",
					"description": "Some Test Tracks Transmission",
					"fallbackplaylist": %d,
					"slottype": "simplelive",
					"beginningtime": {
						"year": 2010,
						"month": 7,
						"day": 1,
						"hour": 10,
						"minute": 0
					},
					"duration": 60,
					"slotparams": {
						"livepassword": "buuuu"
					},
					"comment": "Bad Music Show",
					"tags": "me, justatest"
			}
		}
		""" % (sessionid, pid)
		timeslot = processandcheck(jsonrequest, ret = "timeslot")
		tid = timeslot['id']
		
		jsonrequest = """
		{
			"request": "edittimeslot",
			"username": "foobar",
			"sessionid": "%s",
			"timeslot" : {
					"id": %d,
					"title": "Modified Test Timeslot"
			}
		}
		""" % (sessionid, tid)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"sessionid": "%s",
			"timeslot" : {
					"title": "Test"
			}
		}
		""" % sessionid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"sessionid": "%s",
			"timeslot" : {
					"comment": "booo"
			}
		}
		""" % sessionid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"sessionid": "%s",
			"timeslot" : {
					"from": {
						"year": 1970
					},
					"to":{
						"year": 2010,
						"month": 12
					}
			}
		}
		""" % sessionid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"sessionid": "%s",
			"timeslot": {
				"id": %d
			}
		}
		""" % (sessionid, tid)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "edittimeslot",
			"username": "foobar",
			"sessionid": "%s",
			"timeslot" : {
					"id": %d,
					"beginningtime": {
						"year": 2010,
						"month": 7,
						"day": 1,
						"hour": 10,
						"minute": 30
					},
					"duration": 60
			}
		}
		""" % (sessionid, tid)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unreservetimeslot",
			"username": "foobar",
			"sessionid": "%s",
			"timeslotid" : %d
		}""" % (sessionid, tid)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeplaylist",
			"username": "foobar",
			"sessionid": "%s",
			"playlistid": %d
		}
		""" % (sessionid, pid)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafileid": %d
		}
		""" % (sessionid, id1)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "foobar",
			"sessionid": "%s",
			"mediafileid": %d
		}
		""" % (sessionid, id2)
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"sessionid": "%s",
			"name": "testuser"
		}
		""" % sessionid
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"sessionid": "%s",
			"rolename": "testrole"
		}
		""" % sessionid
		processandcheck(jsonrequest)

def logouttest(sessionid):
		jsonrequest = """
		{
			"request": "logout",
			"username": "foobar",
			"sessionid": "%s"
		}
		""" % sessionid
		return processandcheck(jsonrequest)

# Perform some tests on the JSON interface
jp = jsonif.JSONProcessor()
login = logintest()
roletest(login)
usertest(login)
mediafiletest(login)
playlisttest(login)
timeslottest(login)
logouttest(login)


