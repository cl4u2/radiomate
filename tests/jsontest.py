# vim:fileencoding=utf-8:nomodified

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

def roletest():
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
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "getrole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "listroles",
			"username": "foobar",
			"password": "secret"
		}
		"""
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testroule"
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		processandcheck(jsonrequest)

def usertest():
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
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"password": "secret",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		"""
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "getuser",
			"username": "foobar",
			"password": "secret",
			"name": "testuser"
		}
		"""
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "listusers",
			"username": "testuser",
			"password": "secrettest"
		}
		"""
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"password": "secret",
			"name": "testusser"
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"password": "secret",
			"name": "testuser"
		}
		"""
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		processandcheck(jsonrequest)

def mediafiletest():
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
				"canRegisterFiles": true,
				"canManageRegisteredFiles": true,
				"canSearchRegisteredFiles": true,
				"canManageTimetable": false,
				"fixedSlotTime": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": 60,
				"canCreateTestMountpoint": false,
				"canListNetcasts": false
			}
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"password": "secret",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "foobar",
			"password": "secret",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "testuser",
			"password": "secrettest",
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
		"""
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		print mediafile
		id = mediafile['id']
		
		jsonrequest = """
		{
			"request": "getfile",
			"username": "testuser",
			"password": "secrettest",
			"mediafileid": %d
		}
		""" % id
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		print mediafile
		
		jsonrequest = """
		{
			"request": "searchfiles",
			"username": "testuser",
			"password": "secrettest",
			"mediafile": {
				"path": "ugly/",
				"year": 2010
			}
		}
		"""
		mediafilelist = processandcheck(jsonrequest, ret='mediafilelist')
		print mediafilelist
		
		jsonrequest = """
		{
			"request": "searchfiles",
			"username": "testuser",
			"password": "secrettest",
			"mediafile": {
				"user": "testuser"
			}
		}
		"""
		mediafilelist = processandcheck(jsonrequest, ret='mediafilelist')
		print mediafilelist
		
		jsonrequest = """
		{
			"request": "editfile",
			"username": "testuser",
			"password": "secrettest",
			"mediafile": {
				"id": %d,
				"title": "It Was Just A Test Track"
			}
		}
		""" % id
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		print mediafile
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "testuser",
			"password": "secrettest",
			"mediafileid": %d
		}
		""" % id
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"password": "secret",
			"name": "testuser"
		}
		"""
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		processandcheck(jsonrequest)

def playlisttest():
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"password": "secret",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": true,
				"canRegisterFiles": true,
				"canManageRegisteredFiles": true,
				"canSearchRegisteredFiles": true,
				"canManageTimetable": false,
				"fixedSlotTime": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": 60,
				"canCreateTestMountpoint": false,
				"canListNetcasts": false
			}
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"password": "secret",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "testuser",
			"password": "secrettest",
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
		"""
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id1 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "testuser",
			"password": "secrettest",
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
		"""
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id2 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "createplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlist": {
					"title": "Test Playlist",
					"description": "Some Test Tracks",
					"comment": "Bad Music",
					"tags": "me, justatest",
					"fallback": true,
					"viewers": [ "foobar" ],
					"owners": [ "testuser", "foobar" ]
			}
		}
		"""
		playlist = processandcheck(jsonrequest, ret='playlist')
		pid = playlist['id']
		
		jsonrequest = """
		{
			"request": "addfilestoplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlistid": %d,
			"mediafileidlist": [ %d, %d ]
		}
		""" % (pid, id1, id2)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "movefilesinplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlistid": %d,
			"oldmediafileposition": %d, 
			"newmediafileposition": %d 
		}
		""" % (pid, 1, 0)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removefilesfromplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlistid": %d,
			"mediafilepositionlist": [ 0 ]
		}
		""" % (pid)
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "editplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlist": {
					"id": %d,
					"title": "Modified Playlist"
			}
		}
		""" % pid
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listuserplaylists",
			"username": "testuser",
			"password": "secrettest",
			"user": "admin"
		}
		""" 
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlistid": %d
		}
		""" % pid
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "testuser",
			"password": "secrettest",
			"mediafileid": %d
		}
		""" % id1
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "testuser",
			"password": "secrettest",
			"mediafileid": %d
		}
		""" % id2
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"password": "secret",
			"name": "testuser"
		}
		"""
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		processandcheck(jsonrequest)

def timeslottest():
		jsonrequest = """
		{
			"request": "createrole",
			"username": "foobar",
			"password": "secret",
			"role" : {
				"rolename": "testrole",
				"canManageRoles": false,
				"canManageUsers": false,
				"canManageAllPlaylists": true,
				"canRegisterFiles": true,
				"canManageRegisteredFiles": true,
				"canSearchRegisteredFiles": true,
				"canManageTimetable": false,
				"fixedSlotTime": false,
				"fixedSlotTimesList": "45,90",
				"changeTimeBeforeTransmission": 60,
				"canCreateTestMountpoint": false,
				"canListNetcasts": false
			}
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "createuser",
			"username": "foobar",
			"password": "secret",
			"user" : {
				"name": "testuser",
				"password": "secrettest",
				"displayname": "Test user",
				"rolename": "testrole"
			}
		}
		"""
		processandcheck(jsonrequest, check=False)
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "testuser",
			"password": "secrettest",
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
		"""
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id1 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "registerfile",
			"username": "testuser",
			"password": "secrettest",
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
		"""
		mediafile = processandcheck(jsonrequest, ret='mediafile')
		id2 = mediafile['id']
		
		jsonrequest = """
		{
			"request": "createplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlist": {
					"title": "Test Playlist",
					"description": "Some Test Tracks",
					"comment": "Bad Music",
					"tags": "me, justatest",
					"fallback": true,
					"viewers": [ "foobar" ],
					"owners": [ "testuser", "foobar" ]
			}
		}
		"""
		playlist = processandcheck(jsonrequest, ret='playlist')
		pid = playlist['id']
		
		jsonrequest = """
		{
			"request": "addfilestoplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlistid": %d,
			"mediafileidlist": [ %d, %d ]
		}
		""" % (pid, id1, id2)
		playlist = processandcheck(jsonrequest)


		jsonrequest = """
		{
			"request": "reservetimeslot",
			"username": "foobar",
			"password": "secret",
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
		""" % pid
		timeslot = processandcheck(jsonrequest, ret = "timeslot")
		tid = timeslot['id']
		
		jsonrequest = """
		{
			"request": "edittimeslot",
			"username": "foobar",
			"password": "secret",
			"timeslot" : {
					"id": %d,
					"title": "Modified Test Timeslot"
			}
		}
		""" % tid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"password": "secret",
			"timeslot" : {
					"title": "Test"
			}
		}
		""" 
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"password": "secret",
			"timeslot" : {
					"comment": "booo"
			}
		}
		""" 
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"password": "secret",
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
		""" 
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "listtimeslots",
			"username": "foobar",
			"password": "secret",
			"timeslot": {
				"id": %d
			}
		}
		""" % tid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "edittimeslot",
			"username": "foobar",
			"password": "secret",
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
		""" % tid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unreservetimeslot",
			"username": "foobar",
			"password": "secret",
			"timeslotid" : %d
		}""" % tid
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeplaylist",
			"username": "testuser",
			"password": "secrettest",
			"playlistid": %d
		}
		""" % pid
		playlist = processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "testuser",
			"password": "secrettest",
			"mediafileid": %d
		}
		""" % id1
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "unregisterfile",
			"username": "testuser",
			"password": "secrettest",
			"mediafileid": %d
		}
		""" % id2
		processandcheck(jsonrequest)
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"password": "secret",
			"name": "testuser"
		}
		"""
		processandcheck(jsonrequest)

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		processandcheck(jsonrequest)

# Perform some tests on the JSON interface
jp = jsonif.JSONProcessor()
#roletest()
#usertest()
#mediafiletest()
#playlisttest()
timeslottest()


