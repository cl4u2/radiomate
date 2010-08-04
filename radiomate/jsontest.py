
from jsonif import *


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


# Perform some tests on the JSON interface
jp = RadioMateJSONProcessor()
#roletest()
#usertest()
mediafiletest()


