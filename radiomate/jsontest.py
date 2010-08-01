
from jsonic import *

def roletest():
		jp = RadioMateJSONProcessor()
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
		r = jp.process(jsonrequest)
		print r

		jsonrequest = """
		{
			"request": "getrole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		print jsonrequest
		r = jp.process(jsonrequest)
		print r

		jsonrequest = """
		{
			"request": "listroles",
			"username": "foobar",
			"password": "secret"
		}
		"""
		print jsonrequest
		r = jp.process(jsonrequest)
		print r
		
		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		print jsonrequest
		r = jp.process(jsonrequest)
		print r

def usertest():
		jp = RadioMateJSONProcessor()
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
		r = jp.process(jsonrequest)
		print r
		
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
		print jsonrequest
		r = jp.process(jsonrequest)
		print r
		
		jsonrequest = """
		{
			"request": "getuser",
			"username": "foobar",
			"password": "secret",
			"rolename": "testuser"
		}
		"""
		print jsonrequest
		r = jp.process(jsonrequest)
		print r

		jsonrequest = """
		{
			"request": "listusers",
			"username": "foobar",
			"password": "secret"
		}
		"""
		print jsonrequest
		r = jp.process(jsonrequest)
		print r
		
		jsonrequest = """
		{
			"request": "removeuser",
			"username": "foobar",
			"password": "secret",
			"name": "testuser"
		}
		"""
		print jsonrequest
		r = jp.process(jsonrequest)
		print r

		jsonrequest = """
		{
			"request": "removerole",
			"username": "foobar",
			"password": "secret",
			"rolename": "testrole"
		}
		"""
		print jsonrequest
		r = jp.process(jsonrequest)
		print r


# Perform some tests on the JSON interface
#roletest()
usertest()
