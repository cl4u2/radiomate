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
import datetime

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
				# check value and set it
				def recursetattr(dictionary, name, newvalue):
						# check correctness of name
						if not name in dictionary.keys():
								raise RadioMateException("wrong parameter name: %s" % name)

						dictvalue = dictionary[name]

						if isinstance(dictvalue, dict) and isinstance(newvalue, dict):
								d = {}
								for k, v in newvalue.iteritems():
										ke, va = recursetattr(dictvalue, k, v)
										d.update({ke: va})
								return (name, d)
						elif type(dictvalue) == type(newvalue):
								return (name, newvalue)
						elif isinstance(dictvalue, bool) and isinstance(newvalue, int):
								return (name, newvalue != 0)
						elif isinstance(dictvalue, int) and isinstance(newvalue, long):
								return (name, int(newvalue))
						elif isinstance(dictvalue, long) and isinstance(newvalue, int):
								return (name, newvalue)
						elif isinstance(dictvalue, str) and isinstance(newvalue, unicode):
								return (name, str(newvalue))
						elif isinstance(dictvalue, unicode) and isinstance(newvalue, str):
								return (name, str(newvalue))
						elif isinstance(dictvalue, int) and isinstance(newvalue, basestring):
								return (name, int(newvalue))
						else:
								raise RadioMateException("wrong parameter type: %s (%s) in %s (%s)" \
												% (newvalue, type(newvalue), name, type(dictvalue)))
				
				try:
						na, va = recursetattr(self.__dict__, name, value)
						self.__setattr(na, va)
				except ValueError:
						raise RadioMateException("Cannot convert %s (%s) to %s" % \
										 (value, type(value), type(self.__dict__[name])))
		
		def __str__(self):
				return str(self.__dict__)
		
		def __repr__(self):
				return str(self)
		
		def dictexport(self):
				def isBaseType(value):
						if isinstance(value, bool) or \
								isinstance(value, int) or \
								isinstance(value, long) or \
								isinstance(value, basestring):
								return True
						else:
								return False

				def xport(k, v):
						if isBaseType(v):
								if k:
										return {k: v}
								else:
										return v
						elif isinstance(v, list):
								l = []
								for e in v:
										l.append(xport(None, e))
								if k:
										return {k: l}
								else:
										return l
						elif isinstance(v, dict):
								di = {}
								for ke, va in v.iteritems():
										di.update({ke: xport(None, va)})
								if k:
										return {k: di}
								else:
										return di
						else:
								if k:
										return {k: xport(None, v)}
								else:
										try:
												return v.dictexport()
										except:
												return {}

				d = {}
				for k, v in self.__dict__.iteritems():
						if k == "password":
								continue
						if k == "position" and k < 0:
								continue
						d.update(xport(k, v))

				return d

		def dictupdate(self, newdict):
				"merge self.__dict__ with items in newdict"
				assert isinstance(newdict, dict)

				def isBaseType(value):
						if isinstance(value, bool) or \
								isinstance(value, int) or \
								isinstance(value, long) or \
								isinstance(value, basestring):
								return True
						else:
								return False

				def port(k, v):
						if isBaseType(v):
								if k:
										return (k, v)
								else:
										return v
						elif isinstance(v, list):
								l = []
								for e in v:
										l.append(port(None, e))
								if k:
										return (k, l)
								else:
										return l
						elif isinstance(v, dict):
								di = {}
								for ke, va in v.iteritems():
										di.update({ke: port(None, va)})
								if k:
										return (k, di)
								else:
										return di
						else:
								if k:
										return (k, port(None, v))
								else:
										return port(None, v)

				for k, v in newdict.iteritems():
						if k in self.__dict__:
								ke, va = port(k,v)
								setattr(self, ke ,va)


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
								'tags' : '', \
								'position' : -1})
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
				if isinstance(value, list) and name == "mediafilelist" or name == "owners" or name == "viewers":
						r = RadioMateParentClass.__setattr__(self, name, value)
						self.__posUpdate()
						return r
				return RadioMateParentClass.__setattr__(self, name, value)

		def __posUpdate(self):
				for i, mf in enumerate(self.mediafilelist):
						mf.position = i

		def addMediaFile(self, mediafile):
				if isinstance(mediafile, MediaFile):
						self.mediafilelist.append(mediafile)
						self.__posUpdate()
				else:
						raise RadioMateException("MediaFile object expected")

		def removeMediaFile(self, playlistposition):
				try:
						del self.mediafilelist[playlistposition]
						self.__posUpdate()
				except:
						raise RadioMateException("position out of range")

		def clearMediaFileList(self):
				RadioMateParentClass.__setattr__(self, "mediafilelist", [])

		def addOwner(self, username):
				if isinstance(username, basestring):
						self.owners.append(username)
						RadioMateParentClass.__setattr__(self, "owners", list(set(self.owners)))
				else:
						raise RadioMateException("string expected [%s]" % username)

		def removeOwner(self, username):
				if isinstance(username, basestring):
						ownset = set(self.owners)
						ownset.remove(username)
						RadioMateParentClass.__setattr__(self, "owners", list(ownset))
				else:
						raise RadioMateException("string expected [%s]" % username)

		def clearOwners(self):
				RadioMateParentClass.__setattr__(self, "owners", [])

		def addViewer(self, username):
				if isinstance(username, basestring):
						self.viewers.append(username)
						RadioMateParentClass.__setattr__(self, "viewers", list(set(self.viewers)))
				else:
						raise RadioMateException("string expected [%s] % username")
		
		def removeViewer(self, username):
				if isinstance(username, basestring):
						viewset = set(self.viewers)
						viewset.remove(username)
						RadioMateParentClass.__setattr__(self, "viewers", list(viewset))
				else:
						raise RadioMateException("string expected [%s]" % username)
		
		def clearViewers(self):
				RadioMateParentClass.__setattr__(self, "viewers", [])


class TimeSlot(RadioMateParentClass):
		"This entity class represents the timeslot reserved for a show"
		def __init__(self, classdict = {}):
				"take as parameter a row dictionary obtained through a MySQLdb.cursors.DictCursor object, or a json string"
				self.__dict__.update({
								'id': 0L,\
								'creator' : '',\
								'slottype' : '',\
								'slotparams' : {},\
								'beginningtime': {
										'year' : 0,\
										'month' : 0,\
										'day' : 0,\
										'hour' : 0,\
										'minute' : 0\
								 }, \
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
				ymdhm = ['year', 'month', 'day', 'hour', 'minute']

				if name == "slotparams" and isinstance(value, dict):
						for k,v in value.iteritems():
								self.__dict__['slotparams'].update({k.encode('ascii'): v})
						return

				if name == "beginningtime" and (isinstance(value, int) or isinstance(value, long)):
						# convert unix timestamp to internal representation
						ttuple = time.localtime(value)
						d = {}
						for k, v in zip(ymdhm, ttuple[:5]):
								d.update({k: v})
						return RadioMateParentClass.__setattr__(self, "beginningtime", d)

				if name == "beginningtime":
						for k in ymdhm:
								if not value.has_key(k):
										value[k] = 0

				return RadioMateParentClass.__setattr__(self, name, value)

		def getBeginningTimestamp(self):
				"convert to unix timestamp"
				timetuple = (self.beginningtime['year'],\
								self.beginningtime['month'],\
								self.beginningtime['day'],\
								self.beginningtime['hour'],\
								self.beginningtime['minute'],\
								0, -1, -1, -1)
				return time.mktime(timetuple)

		def getEndingTimestamp(self):
				"convert to unix timestamp"
				timetuple = (self.beginningtime['year'],\
								self.beginningtime['month'],\
								self.beginningtime['day'],\
								self.beginningtime['hour'],\
								self.beginningtime['minute'],\
								0, -1, -1, -1)
				t = time.mktime(timetuple)
				t += self.duration * 60 	#seconds in one minute
				return t

		def getBeginningDatetime(self):
				"return a string with the beginning date and time"
				return "%04d-%02d-%02d %02d:%02d" % \
								(self.beginningtime['year'],\
								self.beginningtime['month'],\
								self.beginningtime['day'],\
								self.beginningtime['hour'],\
								self.beginningtime['minute'])

		def getEndingDatetime(self):
				"return a string with the ending date and time"
				ts = self.getEndingTimestamp()
				tt = time.localtime(ts)
				return "%04d-%02d-%02d %02d:%02d" % tt[:5]

		def setBeginningDateTime(self, thetime):
				"given a string in YYYY-MM-DD HH:MM:SS format or a time.struct_time object set the beginning time"
				if isinstance(thetime, time.struct_time):
						tm = thetime
				elif isinstance(thetime, datetime.datetime):
						tm = time.strptime(str(thetime), "%Y-%m-%d %H:%M:%S")
				else:
						tm = time.strptime(str(thetime), "%Y-%m-%d %H:%M:%S")

				self.beginningtime = {'year': tm.tm_year, 'month': tm.tm_mon,\
								'day': tm.tm_mday, 'hour': tm.tm_hour, 'minute': tm.tm_min}
		
		def setEndingDateTime(self, thetime):
				"given a string in YYYY-MM-DD HH:MM:SS format or a time.struct_time object set the duration from the beginning time"
				if isinstance(thetime, time.struct_time):
						tm = thetime
				elif isinstance(thetime, datetime.datetime):
						tm = time.strptime(str(thetime), "%Y-%m-%d %H:%M:%S")
				else:
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
		ts.fallbackplaylist = 3
		b = {"year": 2010, "month": 10, "day": 6, "hour":13, "minute": 30}
		ts.beginningtime = b
		print ts.getBeginningDatetime()
		parms = {"par1": 1, "par2": 2}
		ts.slotparams = parms
		print ts
		xp = ts.dictexport()
		t1 = TimeSlot()
		t1.dictupdate(xp)
		print t1

