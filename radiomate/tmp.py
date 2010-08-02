import dao
from mate import *

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
print udao.insert(u)

