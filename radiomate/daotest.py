# Test of the dao module

import json
from dao import *
import sys

# connection parameters
DBHOST="127.0.0.1"
DBUSER="mate"
DBPASSWORD="radi0"
DATABASE="radiomate0"

def test0():
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
		r.rolename = "scemodelvillaggio"
		roledao.insert(r)
		r.rolename = "scemodelvillaggio2"
		roledao.insert(r)
		r.rolename = "scemodelvillaggio3"
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
		u.name = "foobar3"
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

def roledaotest():
		r = Role()
		r.rolename = "testrole"
		conn = MySQLdb.connect( 
						host = DBHOST, 
						user = DBUSER,
						passwd = DBPASSWORD,
						db = DATABASE
						)
		roledao = RoleMysqlDAO(conn)
		roledao.insert(r)
		r1 = roledao.getByName("testrole")
		print r1
		rall = roledao.getAll()
		print rall
		r1.canManageRoles = True
		roledao.update(r1)
		r2 = roledao.getByName("testrole")
		print r2
		roledao.removeByName("testrole")
		conn.close()

def userdaotest():
		r = Role()
		r.rolename = "testrole"
		conn = MySQLdb.connect( 
						host = DBHOST, 
						user = DBUSER,
						passwd = DBPASSWORD,
						db = DATABASE
						)
		roledao = RoleMysqlDAO(conn)
		roledao.insert(r)
		u = User()
		u.name = "testuser"
		u.displayname = "Test User"
		u.rolename = r.rolename
		userdao = UserMysqlDAO(conn)
		userdao.insert(u)
		u1 = userdao.getByName(u.name)
		print u1
		u1.displayname = "Modified Test User"
		userdao.update(u1)
		u2 = userdao.getByName(u1.name)
		print u2
		res = userdao.getAll()
		print res
		userdao.removeByName(u.name)
		roledao.removeByName(r.rolename)

def mediafilesdaotest():
		r = Role()
		r.rolename = "testrole"
		u = User()
		u.name = "foobar"
		u.rolename = r.rolename

		mf = MediaFile()
		mf.user = u.name
		mf.path = "/tmp/ulululu.mp3"
		mf.type = 'audio'
		mf.title = "Ulululu"
		mf.author = "Shakerobba"
		mf.album = "Steam this album"
		mf.genre = "steam pop"
		mf.year = 1932
		mf.comment = "very good music"
		mf.license = "CC"
		mf.tags = "shakerobba,steam,wolves"
		conn = MySQLdb.connect( 
						host = DBHOST, 
						user = DBUSER,
						passwd = DBPASSWORD,
						db = DATABASE
						)
		rdao = RoleMysqlDAO(conn)
		rdao.insert(r)

		udao = UserMysqlDAO(conn)
		udao.insert(u)
		mediafiledao = MediaFileMysqlDAO(conn)
		id = mediafiledao.insert(mf)
		mf2 = mediafiledao.getById(id)
		print mf2
		mf2.license = "AGPL"
		mediafiledao.update(mf2)
		mf3 = mediafiledao.getById(id)
		print mf3
		mediafiledao.removeById(id)
		udao.removeByName(u.name)
		rdao.removeByName(r.rolename)

def playlistdaotest():
		conn = MySQLdb.connect( 
						host = DBHOST, 
						user = DBUSER,
						passwd = DBPASSWORD,
						db = DATABASE
						)
		r = Role()
		r.rolename = "testrole"
		rdao = RoleMysqlDAO(conn)
		rdao.insert(r)
		u1 = User()
		u1.name = "foobar"
		u1.rolename = r.rolename
		udao = UserMysqlDAO(conn)
		udao.insert(u1)
		u2 = User()
		u2.name = "foobar2"
		u2.rolename = r.rolename
		udao.insert(u2)

		mf = MediaFile()
		mf.user = "foobar2"
		mf.path = "/tmp/ulululu.mp3"
		mf.type = 'audio'
		mf.title = "Ulululu"
		mf.author = "Shakerobba"
		mf.album = "Steam this album"
		mf.genre = "steam pop"
		mf.year = 1932
		mf.comment = "very good music"
		mf.license = "CC"
		mf.tags = "shakerobba,steam,wolves"

		mf2 = MediaFile()
		mf2.user = "foobar2"
		mf2.path = "/tmp/ulululu2.mp3"
		mf2.type = 'audio'
		mf2.title = "Ulululu2"
		mf2.author = "Shakerobba"
		mf2.album = "Steam this album"
		mf2.genre = "steam pop"
		mf2.year = 1932
		mf2.comment = "very good music"
		mf2.license = "CC"
		mf2.tags = "shakerobba,steam,wolves,sequel"
		
		mediafiledao = MediaFileMysqlDAO(conn)
		id1 = mediafiledao.insert(mf)
		id2 = mediafiledao.insert(mf2)
		mf = mediafiledao.getById(id1)
		mf2 = mediafiledao.getById(id2)

		pl = PlayList()
		pl.title = "just a test"
		pl.creator = "foobar2"
		pl.fallback = False
		pl.description = "testing dao"
		pl.comment = ":)"
		pl.tags = "test,prova,foo,bar"

		pl.addMediaFile(mf)
		pl.addMediaFile(mf2)
		
		pl.addOwner("foobar")
		pl.addViewer("foobar2")

		print pl

		playlistdao = PlayListMysqlDAO(conn)
		plid = playlistdao.insert(pl)
		print plid
		pl2 = playlistdao.getById(plid)
		print pl2

		pl2.description = "testing dao 2"
		playlistdao.update(pl2)
		pl3 = playlistdao.getById(pl2.id)
		print pl3

		res = playlistdao.getByUser("foobar")
		print res

		res = playlistdao.getByCreator("foobar2")
		print res

		mediafiledao.removeById(id1)
		mediafiledao.removeById(id2)
		playlistdao.removeById(plid)
		udao.removeByName(u1.name)
		udao.removeByName(u2.name)
		rdao.removeByName(r.rolename)
		conn.close()

def timeslotdaotest():
		conn = MySQLdb.connect( 
						host = DBHOST, 
						user = DBUSER,
						passwd = DBPASSWORD,
						db = DATABASE
						)
		r = Role()
		r.rolename = "testrole"
		rdao = RoleMysqlDAO(conn)
		rdao.insert(r)
		udao = UserMysqlDAO(conn)
		u1 = User()
		u1.name = "foobar"
		u1.rolename = "testrole"
		udao.insert(u1)
		u2 = User()
		u2.name = "foobar2"
		u2.rolename = "testrole"
		udao.insert(u2)

		ts = TimeSlot()
		ts.creator = 'foobar'
		ts.slottype = 'dummy'
		ts.slotparams = {'par1': 0, 'par2': 'ciao'}
		ts.beginningyear = 2010
		ts.beginningmonth = 07
		ts.beginningday = 1
		ts.beginninghour = 10
		ts.beginningminute = 0
		ts.duration = 60
		ts.title = "The Test Show"
		ts.description = "the best test show ever"
		ts.comment = "just a test"
		ts.tags = "test, show, radio"
		
		pl = PlayList()
		pl.title = "just a test"
		pl.creator = "foobar2"
		pl.fallback = False
		pl.description = "testing dao"
		pl.comment = ":)"
		pl.tags = "test,prova,foo,bar"
		playlistdao = PlayListMysqlDAO(conn)
		plid = playlistdao.insert(pl)

		ts.fallbackplaylist = plid

		tsdao = TimeSlotMysqlDAO(conn)
		tsid = tsdao.insert(ts)

		ts1 = tsdao.getById(tsid)
		ts1.description = "testing dao"
		tsdao.update(ts1)

		ts2 = tsdao.getById(tsid)
		print ts2

		res = tsdao.getFromTo("2010-07-01 9:00", "2010-07-01 12:00")
		print res

		tss = TimeSlot()
		tss.title = "show"
		res = tsdao.search(tss)
		print res
		
		tsdao.removeById(tsid)
		playlistdao.removeById(plid)
		udao.removeByName(u1.name)
		udao.removeByName(u2.name)
		rdao.removeByName(r.rolename)
		conn.close()

def exceptiontest():
		conn = MySQLdb.connect( 
						host = DBHOST, 
						user = DBUSER,
						passwd = DBPASSWORD,
						db = DATABASE
						)
		try:
				selstring = "SELECT dummyfield FROM roles"
				cursor = conn.cursor(MySQLdb.cursors.DictCursor)
				cursor.execute(selstring)
				cursor.close()
		except MySQLdb.Error, e:
				raise RadioMateDAOException(e.args)
		
		conn.close()


#execute
print "---"
#test0()
#roledaotest()
#userdaotest()
#mediafilesdaotest()
#playlistdaotest()
timeslotdaotest()
#exceptiontest()

