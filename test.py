import sys
import MySQLdb
import json

class RadioMateException(Exception):
		"Just a generic Exception class"
		pass

class RadioMateParentClass(object):
		"The parent class from which the other classes representing entities inherit"
		def __setattr(self, name, value):
				if isinstance(value, basestring):
						realvalue = unicode(value)
				else:
						realvalue = value
				self.__dict__[name.encode('ascii')] = realvalue

		def __setattr__(self, name, value):
						# check correctness of name
						if not name in self.__dict__.keys():
								raise RadioMateException("Wrong parameter name: %s" % name)
						# check value and insert it
						if self.__dict__[name].__class__ == value.__class__:
								self.__setattr(name, value)
						elif isinstance(self.__dict__[name], bool) and isinstance(value, int):
								self.__setattr(name, value != 0)
						elif isinstance(self.__dict__[name], int) and isinstance(value, long):
								self.__setattr(name, int(value))
						elif isinstance(self.__dict__[name], str) and isinstance(value, unicode):
								self.__setattr(name, str(value))
						else:
								raise RadioMateException("Wrong parameter type: %s (%s) in %s (%s)" \
												% (value, value.__class__, name, self.__dict__[name].__class__))
		
		def __str__(self):
				return str(self.__dict__)

		def dictexport(self):
				d = {}
				for k, v in self.__dict__.iteritems():
						if isinstance(self.__dict__[k], bool) or \
								isinstance(self.__dict__[k], int) or \
								isinstance(self.__dict__[k], long) or \
								isinstance(self.__dict__[k], basestring):
										d.update({k:v})
				return d




class Role(RadioMateParentClass):
		"This entity class represents the roles of the users"
		def __init__(self, classdict = {}):
				"take as parameter a row dictionary obtained through a MySQLdb.cursors.DictCursor object, or a json string"
				# TODO: check a priori for the correctness of classdict?
				self.__dict__.update({'rolename' : '',\
								'canManageRoles' : False,\
								'canManageUsers' : False,\
								'canManageAllPlaylists' : False,\
								'canRegisterFiles' : False,\
								'canManageRegisteredFiles' : False,\
								'canSearchRegisteredFiles' : False,\
								'canManageTimetable' : False, \
								'fixedSlotTime' : False, \
								'changeTimeBeforeTransmission' : 1440, \
								'canCreateTestMountpoint' : False, \
								'canListNetcasts' : False, \
								'fixedSlotTimesList' : "60,120"})
				RadioMateParentClass.__init__(self)
				for k,v in classdict.iteritems(): 
						self.__setattr__(k, v)

		def fixedSlotTimesListList(self):
				return [int(s) for s in self.fixedSlotTimesList.strip("[]").split(",")]


class User(RadioMateParentClass):
		"This entity class represents the users"
		def __init__(self, classdict = {}):
				"take as parameter a row dictionary obtained through a MySQLdb.cursors.DictCursor object, or a json string"
				# TODO: check a priori for the correctness of classdict?
				self.__dict__.update({'name' : '',\
								'password' : '',\
								'displayname' : '',\
								'rolename' : ''})
				RadioMateParentClass.__init__(self)
				for k,v in classdict.iteritems(): 
						self.__setattr__(k, v)

		def __setattr__(self, name, value):
				try:
						return RadioMateParentClass.__setattr__(self, name, value)
				except RadioMateException:
						pass
				if name != "role":
						raise RadioMateException("Wrong parameter name: %s" % name)
				if isinstance(value, basestring):
						return RadioMateParentClass.__setattr__(self, "rolename", value)
				if not isinstance(value, Role):
						raise RadioMateException("Wrong parameter type: %s (%s) in role (Role)" \
										% (value, value.__class__))
				object.__setattr__(self, name, value)
						



class RadioMateParentMysqlDAO(object):
		"The parent class from which the other classess representing MySQL Database Access Objects (DAOs) inherit"
		def __init__(self, connection):
				if isinstance(connection, MySQLdb.connections.Connection):
						self.conn = connection
				else:
						raise RadioMateException("Is not a MySQL connection: %s", self.conn)


class RoleMysqlDAO(RadioMateParentMysqlDAO):
		"The MySQL Database Access Object for Roles"
		def __insert(self, roleobject, cursor):
				insertionstring = """
				INSERT INTO roles (
						rolename, 
						canManageRoles, 
						canManageUsers,
						canManageAllPlaylists,
						canRegisterFiles,
						canManageRegisteredFiles,
						canSearchRegisteredFiles,
						canManageTimetable,
						fixedSlotTime,
						changeTimeBeforeTransmission,
						canCreateTestMountpoint,
						canListNetcasts,
						fixedSlotTimesList
				) VALUES (
				'%s', %d, %d, %d, %d, %d, %d, %d, %d, %d , %d, %d, '%s')""" % (
						roleobject.rolename,
						int(roleobject.canManageRoles),
						int(roleobject.canManageUsers),
						int(roleobject.canManageAllPlaylists),
						int(roleobject.canRegisterFiles),
						int(roleobject.canManageRegisteredFiles),
						int(roleobject.canSearchRegisteredFiles),
						int(roleobject.canManageTimetable),
						int(roleobject.fixedSlotTime),
						roleobject.changeTimeBeforeTransmission,
						int(roleobject.canCreateTestMountpoint),
						int(roleobject.canListNetcasts),
						roleobject.fixedSlotTimesList.strip("[]")
				)
				#debug
				print insertionstring
				cursor.execute(insertionstring)

		def __getByName(self, rolename, cursor):
				selectionstring = """
				SELECT  
						rolename, 
						canManageRoles, 
						canManageUsers,
						canManageAllPlaylists,
						canRegisterFiles,
						canManageRegisteredFiles,
						canSearchRegisteredFiles,
						canManageTimetable,
						fixedSlotTime,
						changeTimeBeforeTransmission,
						canCreateTestMountpoint,
						canListNetcasts,
						fixedSlotTimesList
				FROM roles
				WHERE rolename = '%s'""" % rolename
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def __removeByName(self, rolename, cursor):
				deletionstring = """
				DELETE FROM roles
				WHERE rolename = '%s'""" % rolename
				#debug
				print deletionstring
				cursor.execute(deletionstring)
		
		def __getAll(self, cursor):
				selectionstring = """
				SELECT  
						rolename, 
						canManageRoles, 
						canManageUsers,
						canManageAllPlaylists,
						canRegisterFiles,
						canManageRegisteredFiles,
						canSearchRegisteredFiles,
						canManageTimetable,
						fixedSlotTime,
						changeTimeBeforeTransmission,
						canCreateTestMountpoint,
						canListNetcasts,
						fixedSlotTimesList
				FROM roles"""
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def insert(self, roleobject):
				try:
						cursor = self.conn.cursor()
						self.__insert(roleobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of role rows inserted: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])
		
		def getByName(self, rolename):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getByName(rolename, cursor)
						cursor.close()

						#debug
						print "Number of role rows fetched: %d" % len(resultdicts)
						assert len(resultdicts) == 1
						#debug

						return Role(resultdicts[0])
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def removeByName(self, rolename):
				try:
						cursor = self.conn.cursor()
						self.__removeByName(rolename, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of role rows deleted: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def getAll(self):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getAll(cursor)
						cursor.close()

						#debug
						print "Number of role rows fetched: %d" % len(resultdicts)

						res = []
						for rd in resultdicts:
								res.append(Role(rd))

						return res
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])


class UserMysqlDAO(RadioMateParentMysqlDAO):
		"The MySQL Database Access Object for Users"
		def __insert(self, userobject, cursor):
				# rolename existance check is provided by foreign key in MySQL 
				insertionstring = """
				INSERT INTO users (
						name,
						password,
						displayname,
						role
				) VALUES (
				'%s', '%s', '%s', '%s')""" % (
						userobject.name,
						userobject.password,
						userobject.displayname,
						userobject.rolename
				)
				#TODO: store MD5SUMS of passwords instead of cleartext
				#debug
				print insertionstring
				cursor.execute(insertionstring)

		def __getByName(self, username, cursor):
				selectionstring = """
				SELECT  
						name,
						password,
						displayname,
						role
				WHERE name = '%s'""" % username
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def __removeByName(self, username, cursor):
				deletionstring = """
				DELETE FROM users 
				WHERE name = '%s'""" % username
				#debug
				print deletionstring
				cursor.execute(deletionstring)
		
		def __getAll(self, cursor):
				selectionstring = """
				SELECT  
						name,
						password,
						displayname,
						role
				FROM users"""
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def insert(self, userobject):
				try:
						cursor = self.conn.cursor()
						self.__insert(userobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of user rows inserted: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])
		
		def getByName(self, username):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getByName(username, cursor)
						cursor.close()

						#debug
						print "Number of user rows fetched: %d" % len(resultdicts)
						assert len(resultdicts) == 1
						#debug

						u = User(resultdicts[0])
						roledao = RoleMysqlDAO()
						u.role = roledao.getByName(u.rolename)
						return u
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def removeByName(self, username):
				try:
						cursor = self.conn.cursor()
						self.__removeByName(username, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of user rows deleted: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def getAll(self):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getAll(cursor)
						cursor.close()

						#debug
						print "Number of user rows fetched: %d" % len(resultdicts)

						roledao = RoleMysqlDAO(self.conn)
						res = []
						for rd in resultdicts:
								u = User(rd)
								u.role = roledao.getByName(u.rolename)
								res.append(u)

						return res
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])


# we don't need this
class RadioMateParentJsonTranslator(object):
		"The parent class from which the other classess for translation to/from JSON, inherit"
		pass


# we don't need this
class RoleJsonTranslator(RadioMateParentJsonTranslator):
		"Role object translation to/from JSON"
		@staticmethod
		def fromJSON(jsonstring):
				if not isinstance(jsonstring, basestring):
						raise RadioMateException("fromJSON to Role: wrong argument, string needed")
				try:
						jd = json.loads(jsonstring)
						r = Role(jd)
				except ValueError, e:
						raise RadioMateException("fromJSON to Role: problems with JSON string (%s: %s)" % (e.args[0], e.args[1]))
				return r

		@staticmethod
		def toJSON(roleobject):
				if not isinstance(roleobject, Role):
						raise RadioMateException("from Role toJSON: wrong argument, Role object needed")
				de = roleobject.dictexport()
				return json.dumps(de, skipkeys=True)


# do we need this?
class RoleJsonEncoder(json.JSONEncoder):
		def default(self, obj):
				if isinstance(obj, Role):
						return obj.dictexport()


# MAIN
# connection parameters
DBHOST="127.0.0.1"
DBUSER="mate"
DBPASSWORD="radi0"
DATABASE="radiomate0"

try:
		conn = MySQLdb.connect( 
						host = DBHOST, 
						user = DBUSER,
						passwd = DBPASSWORD,
						db = DATABASE
						)
		cursor = conn.cursor()
		cursor.execute("""INSERT IGNORE INTO roles (
				rolename, 
				canManageRoles, 
				canManageUsers,
				canManageAllPlaylists,
				canRegisterFiles,
				canManageRegisteredFiles,
				canSearchRegisteredFiles,
				canManageTimetable,
				fixedSlotTime,
				changeTimeBeforeTransmission,
				canCreateTestMountpoint,
				canListNetcasts,
				fixedSlotTimesList
				) VALUES (
				'admin',
				1, 1, 1, 1, 1, 1, 1, 1, 120, 1, 1, '60,120')""")
		conn.commit()
		print "Number of rows inserted: %d" % cursor.rowcount
		cursor.close()
		cursor = conn.cursor(MySQLdb.cursors.DictCursor)
		cursor.execute("SELECT * from roles")
		rows = cursor.fetchall()
		print len(rows), "rows fetched"
		for row in rows:
				print ">", row
				r = Role(row)
				print "<", r
				print "-->", r.rolename
		cursor.close()
		conn.close()
				
except MySQLdb.Error, e:
		print "Error %d: %s" % (e.args[0], e.args[1])
		sys.exit(1)

# JSON
jsonrequest = """
{
	"request": "createrole",
	"username": "pippo",
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

try:
		d = json.loads(jsonrequest)
except ValueError, e:
		raise SystemExit("JSON Validation error: %s" % (e))

print "-----"
print d['role']
print "-----"
r = Role(d['role'])
print r
print "-----"
print "-->", r.rolename

print "------>"
print json.dumps(r.dictexport(), skipkeys=True)

print "-----"
r = Role()
print r
print "-->", r.rolename
r.rolename = "scemodelvillaggio3"
print "-->", r.rolename
print "-----"

#DAO
conn = MySQLdb.connect( 
				host = DBHOST, 
				user = DBUSER,
				passwd = DBPASSWORD,
				db = DATABASE
				)
roledao = RoleMysqlDAO(conn)
roledao.insert(r)
r = roledao.getByName("admin")
print r
r = roledao.getByName("scemodelvillaggio")
print r
r = roledao.getByName("scemodelvillaggio2")
print r
r = roledao.getByName("scemodelvillaggio3")
print r
print r.fixedSlotTimesList, r.fixedSlotTimesListList()
roledao.removeByName("scemodelvillaggio3")
rl = roledao.getAll()
for r in rl:
		print r

print "+++++++++++++++++++++++++++++++++++++"
u = User()
u.name = "pippo3"
u.password = "segreta"
u.displayname = "Mr. Pippo 3"
u.rolename = "scemodelvillaggio2"
print u
udao = UserMysqlDAO(conn)
udao.insert(u)
ulist = udao.getAll()
for u in ulist:
		print u
udao.removeByName(u.name)


