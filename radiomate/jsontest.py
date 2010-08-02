
from jsonif import *


def processandcheck(jsonrequest):
		print jsonrequest
		r = jp.process(jsonrequest)
		print r
		rd = json.loads(r)
		if int(rd['responsen']) != 0:
				print rd
				print rd['responsen']
				raise SystemExit("Test Failed")


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
			"username": "foobar",
			"password": "secret"
		}
		"""
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
roletest()
usertest()

