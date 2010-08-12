# vim:fileencoding=utf-8:nomodified
# $Id$

from radiomate import dao
from radiomate.mate import *

DBHOST="127.0.0.1"
DBUSER="mate"
DBPASSWORD="radi0"
DATABASE="radiomate0"

cm = dao.DBConnectionManager(
				dbhost = DBHOST, 
				dbuser = DBUSER,
				dbpassword = DBPASSWORD,
				database = DATABASE
				)
udao = dao.UserDAO(cm)
u = User()
u.name = "foobar"
u.password = "secret"
u.displayname = "Foo Bar"
u.rolename = "admin"
#print udao.insert(u)

mdao = dao.MediaFileDAO(cm)
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
id = mdao.insert(mf)
mf.id = id
print id
		
mf2 = MediaFile()
mf2.user = u.name
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
id = mdao.insert(mf2)
mf2.id = id
print id

pdao = dao.PlayListDAO(cm)
pl = PlayList()
pl.title = "just a test"
pl.creator = u.name
pl.fallback = False
pl.description = "testing dao"
pl.comment = ":)"
pl.tags = "test,prova,foo,bar"

pl.addMediaFile(mf)
pl.addMediaFile(mf2)
print pl
print pl.mediafilelist
		
print pdao.insert(pl)

