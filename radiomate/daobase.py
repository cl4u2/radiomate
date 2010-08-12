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

# Basic DAO Classes

class RadioMateBadTimeSlotException(Exception):
		"Exception to raise if a timeslot cannot fit into the radio's timetable"
		pass


class RadioMateDAOException(Exception):
		"Exception to raise if there are problems interacting with the database"
		pass

class RadioMateConnectionManager(object):
		"Object to manage the connection to the database"
		def __init__(self, dbhost, dbuser, dbpassword, database):
				"to be extended"
				self.dbhost = dbhost
				self.dbuser = dbuser
				self.dbpassword = dbpassword
				self.database = database


