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

import sys
import time

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
								raise RadioMateException("wrong parameter name: %s" % name)
						# check value and insert it
						try:
								if type(self.__dict__[name]) == type(value):
										self.__setattr(name, value)
								elif isinstance(self.__dict__[name], bool) and isinstance(value, int):
										self.__setattr(name, value != 0)
								elif isinstance(self.__dict__[name], int) and isinstance(value, long):
										self.__setattr(name, int(value))
								elif isinstance(self.__dict__[name], str) and isinstance(value, unicode):
										self.__setattr(name, str(value))
								elif isinstance(self.__dict__[name], unicode) and isinstance(value, str):
										self.__setattr(name, str(value))
								elif isinstance(self.__dict__[name], int) and isinstance(value, basestring):
										self.__setattr(name, int(value))
								else:
										raise RadioMateException("wrong parameter type: %s (%s) in %s (%s)" \
														% (value, type(value), name, type(self.__dict__[name])))
						except ValueError:
										raise RadioMateException("Cannot convert %s (%s) to %s" % \
														 (value, type(value), type(self.__dict__[name])))
		
		def __str__(self):
				return str(self.__dict__)
		
		def __repr__(self):
				return str(self)

		def dictexport(self):
				d = {}
				for k, v in self.__dict__.iteritems():
						if k == "password":
								continue
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
				except RadioMateException, e:
						pass
				if name != "role":
						raise RadioMateException("Wrong parameter name: %s" % name)
				if isinstance(value, basestring):
						return RadioMateParentClass.__setattr__(self, "rolename", value)
				if not isinstance(value, Role):
						raise RadioMateException("Wrong parameter type: %s (%s) in role (Role)" \
										% (value, type(value)))
				object.__setattr__(self, name, value)
		

class MediaFile(RadioMateParentClass):
		"This entity class represents a media file"
		def __init__(self, classdict = {}):
				"take as parameter a row dictionary obtained through a MySQLdb.cursors.DictCursor object, or a json string"
				self.__dict__.update({
								'id': 0L,\
								'user' : '',\
								'path' : '',\
								'type' : 'audio',\
								'title' : '',\
								'author' : '',\
								'album' : '',\
								'genre' : '',\
								'year' : 0, \
								'comment' : '', \
								'license' : '', \
								'tags' : ''})
				RadioMateParentClass.__init__(self)
				for k,v in classdict.iteritems(): 
						self.__setattr__(k, v)


class PlayList(RadioMateParentClass):
		"This entity class represents a playlist"
		def __init__(self, classdict = {}):
				"take as parameter a row dictionary obtained through a MySQLdb.cursors.DictCursor object, or a json string"
				self.__dict__.update({
								'id': 0L,\
								'creator' : '',\
								'mediafilelist' : [],\
								'owners' : [],\
								'viewers' : [],\
								'fallback' : False,\
								'title' : '',\
								'description' : '',\
								'comment' : '',\
								'tags' : ''})
				RadioMateParentClass.__init__(self)
				for k,v in classdict.iteritems(): 
						self.__setattr__(k, v)

		def __setattr__(self, name, value):
				if name == "mediafilelist" or name == "owners" or name == "viewers":
						raise RadioMateException("please use the appropriate accessor method")
				return RadioMateParentClass.__setattr__(self, name, value)

		def addMediaFile(self, mediafile):
				if isinstance(mediafile, MediaFile):
						self.mediafilelist.append(mediafile)
				else:
						raise RadioMateException("MediaFile object expected")

		def addOwner(self, username):
				if isinstance(username, basestring):
						self.owners.append(username)
				else:
						raise RadioMateException("string expected")
		
		def addViewer(self, username):
				if isinstance(username, basestring):
						self.viewers.append(username)
				else:
						raise RadioMateException("string expected")
						

class TimeSlot(RadioMateParentClass):
		"This entity class represents the timeslot reserved for a show"
		def __init__(self, classdict = {}):
				"take as parameter a row dictionary obtained through a MySQLdb.cursors.DictCursor object, or a json string"
				self.__dict__.update({
								'id': 0L,\
								'creator' : '',\
								'slottype' : '',\
								'slotparams' : {},\
								'beginningyear' : 0,\
								'beginningmonth' : 0,\
								'beginningday' : 0,\
								'beginninghour' : 0,\
								'beginningminute' : 0,\
								'duration': 0,\
								'title' : '',\
								'description' : '',\
								'comment' : '',\
								'fallbackplaylist' : 0L,\
								'tags' : ''})
				RadioMateParentClass.__init__(self)
				for k,v in classdict.iteritems(): 
						self.__setattr__(k, v)

		def __setattr__(self, name, value):
				if name == "slotparams" and isinstance(value, dict):
						for k,v in value.iteritems():
								self.__dict__['slotparams'].update({k.encode('ascii'): v})
						return

				try:
					return RadioMateParentClass.__setattr__(self, name, value)
				except RadioMateException:
						pass

				if name != "beginningtime":
						raise RadioMateException("Wrong parameter name: %s" % name)

				if isinstance(value, dict):
						try:
								RadioMateParentClass.__setattr__(self, "beginningyear", value['year'])
								RadioMateParentClass.__setattr__(self, "beginningmonth", value['month'])
								RadioMateParentClass.__setattr__(self, "beginningday", value['day'])
								RadioMateParentClass.__setattr__(self, "beginninghour", value['hour'])
								RadioMateParentClass.__setattr__(self, "beginningminute", value['minute'])
						except KeyError:
								raise RadioMateException("something wrong in date/time format")

				elif isinstance(value, int) or isinstance(value, long):
						# convert unix timestamp to internal representation
						ttuple = time.localtime(value)
						RadioMateParentClass.__setattr__(self, "beginningyear", ttuple[0])
						RadioMateParentClass.__setattr__(self, "beginningmonth", ttuple[1])
						RadioMateParentClass.__setattr__(self, "beginningday", ttuple[2])
						RadioMateParentClass.__setattr__(self, "beginninghour", ttuple[3])
						RadioMateParentClass.__setattr__(self, "beginningminute", ttuple[4])

				raise RadioMateException("Wrong parameter type: %s (%s) in %s (%s)" \
								% (value, type(value), name, type(self.__dict__[name])))

		def getBeginningTimestamp(self):
				"convert to unix timestamp"
				timetuple = (self.beginningyear,\
								self.beginningmonth,\
								self.beginningday,\
								self.beginninghour,\
								self.beginningminute,\
								0, -1, -1, -1)
				return time.mktime(timetuple)

		def getEndingTimestamp(self):
				"convert to unix timestamp"
				timetuple = (self.beginningyear,\
								self.beginningmonth,\
								self.beginningday,\
								self.beginninghour,\
								self.beginningminute,\
								0, -1, -1, -1)
				t = time.mktime(timetuple)
				t += self.duration * 60 	#seconds in one minute
				return t

		def getBeginningDatetime(self):
				"return a string with the beginning date and time"
				return "%04d-%02d-%02d %02d:%02d" % \
								(self.beginningyear, self.beginningmonth, self.beginningday, self.beginninghour, self.beginningminute)

		def getEndingDatetime(self):
				"return a string with the ending date and time"
				ts = self.getEndingTimestamp()
				tt = time.localtime(ts)
				return "%04d-%02d-%02d %02d:%02d" % tt[:5]

		def setBeginningDateTime(self, thetime):
				"given a string in YYYY-MM-DD HH:MM:SS format set the beginning time"
				tm = time.strptime(str(thetime), "%Y-%m-%d %H:%M:%S")
				self.beginningyear = tm.tm_year
				self.beginningmonth = tm.tm_mon
				self.beginningday = tm.tm_mday
				self.beginninghour = tm.tm_hour
				self.beginningminute = tm.tm_min
		
		def setEndingDateTime(self, thetime):
				"given a string in YYYY-MM-DD HH:MM:SS format set the duration from the beginning time"
				tm = time.strptime(str(thetime), "%Y-%m-%d %H:%M:%S")
				endts = time.mktime(tm)
				startts = self.getBeginningTimestamp()
				self.duration = int((endts - startts)/60)



if __name__ == '__main__':
		pl = PlayList()
		print pl
		pl.addOwner("foobar")
		print pl.owners
		ts = TimeSlot()

