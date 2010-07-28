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

import MySQLdb
import json
from mate import *


class RadioMateBadTimeSlotException(Exception):
		"Exception to raise if a timeslot cannot fit into the radio's timetable"
		pass


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

		def __update(self, roleobject, cursor):
				updatestring = """
				UPDATE roles 
				SET 
						canManageRoles = %d, 
						canManageUsers = %d,
						canManageAllPlaylists = %d,
						canRegisterFiles = %d,
						canManageRegisteredFiles = %d,
						canSearchRegisteredFiles = %d,
						canManageTimetable = %d,
						fixedSlotTime = %d,
						changeTimeBeforeTransmission = %d,
						canCreateTestMountpoint = %d,
						canListNetcasts = %d,
						fixedSlotTimesList = '%s'
				WHERE rolename = '%s' """ % (
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
						roleobject.fixedSlotTimesList.strip("[]"),
						roleobject.rolename
				)
				#debug
				print updatestring
				cursor.execute(updatestring)

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
		
		def update(self, roleobject):
				try:
						cursor = self.conn.cursor()
						self.__update(roleobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of role rows updated: %d" % cursor.rowcount
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

		def __update(self, userobject, cursor):
				updatestring = """
				UPDATE users 
				SET
						password = '%s',
						displayname = '%s',
						role = '%s'
				WHERE name = '%s'""" % (
						userobject.password,
						userobject.displayname,
						userobject.rolename,
						userobject.name
				)
				#TODO: store MD5SUMS of passwords instead of cleartext
				#debug
				print updatestring
				cursor.execute(updatestring)


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

		def update(self, userobject):
				try:
						cursor = self.conn.cursor()
						self.__update(userobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of user rows updated: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])
		

class MediaFileMysqlDAO(RadioMateParentMysqlDAO):
		"The MySQL Database Access Object for media files"
		def __insert(self, mediafileobject, cursor):
				insertionstring = """
				INSERT INTO mediafiles (
						user, 
						path, 
						type,
						title,
						author,
						album,
						genre,
						year,
						comment,
						license,
						tags
				) VALUES (
				'%s', '%s', '%s', '%s', '%s', '%s', '%s', %d, '%s', '%s', '%s')""" % (
						mediafileobject.user,
						mediafileobject.path, 
						mediafileobject.type,
						mediafileobject.title,
						mediafileobject.author,
						mediafileobject.album,
						mediafileobject.genre,
						mediafileobject.year,
						mediafileobject.comment,
						mediafileobject.license,
						mediafileobject.tags
				)
				#debug
				print insertionstring
				cursor.execute(insertionstring)

		def __getLastId(self, cursor):
				selectionstring = """
				SELECT LAST_INSERT_ID() AS lastid 
				"""
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()[0]['lastid']

		def __getById(self, mediafileid, cursor):
				selectionstring = """
				SELECT  
						id,
						user, 
						path, 
						type,
						title,
						author,
						album,
						genre,
						year,
						comment,
						license,
						tags
				FROM mediafiles
				WHERE id = %d""" % mediafileid
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def __removeById(self, mediafileid, cursor):
				deletionstring = """
				DELETE FROM mediafiles
				WHERE id = %d""" % mediafileid
				#debug
				print deletionstring
				cursor.execute(deletionstring)

		def __search(self, partialmediafile, cursor):
				searchstring = """
				SELECT  
						id,
						user, 
						path, 
						type,
						title,
						author,
						album,
						genre,
						year,
						comment,
						license,
						tags
				FROM mediafiles
				"""
				i = 0
				if partialmediafile.user:
						searchstring += "WHERE user LIKE '\%%s\%' " % partialmediafile.user
						i+=1
				if partialmediafile.path:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " path LIKE '\%%s\%' " % partialmediafile.path
				if partialmediafile.title:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " title LIKE '\%%s\%' " % partialmediafile.title
				if partialmediafile.author:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " author LIKE '\%%s\%' " % partialmediafile.author
				if partialmediafile.album:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " album LIKE '\%%s\%' " % partialmediafile.album
				if partialmediafile.genre:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " genre LIKE '\%%s\%' " % partialmediafile.genre
				if partialmediafile.year:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " year = %d " % partialmediafile.year
				if partialmediafile.comment:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " comment LIKE '\%%s\%' " % partialmediafile.comment
				if partialmediafile.license:
						if i:
								searchstring += " AND "
						else:
								searchstring += " WHERE "
						i+=1
						searchstring += " license LIKE '\%%s\%' " % partialmediafile.license
				#TODO: tags
				#debug
				print searchstring
				cursor.execute(searchstring)
				return cursor.fetchall()

		def __update(self, mediafileobject, cursor):
				updatestring = """
				UPDATE mediafiles
				SET
						user = '%s', 
						path = '%s', 
						type = '%s',
						title = '%s',
						author = '%s',
						album = '%s',
						genre = '%s',
						year = %d,
						comment = '%s',
						license = '%s',
						tags = '%s'
				WHERE 
						mediafileobject.id = '%d'
				""" % (
						mediafileobject.user,
						mediafileobject.path, 
						mediafileobject.type,
						mediafileobject.title,
						mediafileobject.author,
						mediafileobject.album,
						mediafileobject.genre,
						mediafileobject.year,
						mediafileobject.comment,
						mediafileobject.license,
						mediafileobject.tags,
						mediafileobject.id
				)
				#debug
				print updatestring 
				cursor.execute(updatestring)

		def insert(self, mediafileobject):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						self.__insert(mediafileobject, cursor)
						self.conn.commit()
						lastid = self.__getLastId(cursor)
						cursor.close()
						#debug
						print "Number of mediafile rows inserted: %d. Last id = %d" % (cursor.rowcount, lastid)
						return lastid
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])
		
		def getById(self, mediafileid):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getById(mediafileid, cursor)
						cursor.close()

						#debug
						print "Number of mediafile rows fetched: %d" % len(resultdicts)
						assert len(resultdicts) == 1
						#debug

						return MediaFile(resultdicts[0])
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def removeById(self, mediafileid):
				try:
						cursor = self.conn.cursor()
						self.__removeById(mediafileid, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of mediafile rows deleted: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def search(self, partialmediafile):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__search(partialmediafile, cursor)
						cursor.close()

						#debug
						print "Number of mediafile rows fetched while searching: %d" % len(resultdicts)
						#debug

						res = []
						for mf in resultdicts:
								res.append(MediaFile(mf))
						return res
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

class PlayListMysqlDAO(RadioMateParentMysqlDAO):
		"The MySQL Database Access Object for playlists"
		def __insert(self, playlistobject, cursor):
				insertionstring = """
				INSERT INTO playlists (
						creator,
						fallback,
						title,
						description,
						comment,
						tags
				) VALUES (
				'%s', %d, '%s', '%s', '%s', '%s')""" % (
						playlistobject.creator,
						int(playlistobject.fallback),
						playlistobject.title,
						playlistobject.description,
						playlistobject.comment,
						playlistobject.tags
				)
				#debug
				print insertionstring
				cursor.execute(insertionstring)
		
		def __getLastId(self, cursor):
				selectionstring = """
				SELECT LAST_INSERT_ID() AS lastid 
				"""
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()[0]['lastid']

		def __insertmediafile(self, playlistid, mediafileid, position, cursor):
				insertionstring = """
				INSERT INTO compilation (
						playlist,
						mediafile,
						position
				) VALUES (
				%d, %d, %d)""" % (
						playlistid,
						mediafileid,
						position
				)
				#debug
				print insertionstring
				cursor.execute(insertionstring)

		def __insertowner(self, playlistid, ownername, cursor):
				insertionstring = """
				INSERT INTO playlistowners (
						playlist,
						user
				) VALUES (
				%d, '%s')""" % (
						playlistid,
						ownername
				)
				#debug
				print insertionstring
				cursor.execute(insertionstring)
		
		def __insertviewer(self, playlistid, viewername, cursor):
				insertionstring = """
				INSERT INTO playlistviewers(
						playlist,
						user
				) VALUES (
				%d, '%s')""" % (
						playlistid,
						viewername
				)
				#debug
				print insertionstring
				cursor.execute(insertionstring)
		
		def __getById(self, playlistid, cursor):
				selectionstring = """
				SELECT  
						creator,
						fallback,
						title,
						description,
						comment,
						tags
				FROM playlists
				WHERE id = %d""" % playlistid
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()
		
		def __getMediaFiles(self, playlistid, cursor):
				selectionstring = """
				SELECT  
						playlist,
						mediafile,
						position
				FROM compilation
				WHERE playlist = %d
				ORDER BY position""" % playlistid 	#TODO: order in ascending order
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()
		
		def __getOwners(self, playlistid, cursor):
				selectionstring = """
				SELECT  
						playlist,
						user
				FROM playlistowners
				WHERE playlist = %d""" % playlistid 
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()
		
		def __getViewers(self, playlistid, cursor):
				selectionstring = """
				SELECT  
						playlist,
						user
				FROM playlistviewers
				WHERE playlist = %d""" % playlistid 
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()
		
		def __removeById(self, playlistid, cursor):
				deletionstring = """
				DELETE FROM playlists
				WHERE id = %d""" % playlistid #TODO: check if CASCADE is well set in the SQL
				#debug
				print deletionstring
				cursor.execute(deletionstring)

		def __update(self, playlistobject, cursor):
				updatestring = """
				UPDATE playlists
				SET
						creator = '%s',
						fallback = %d,
						title = '%s',
						description = '%s',
						comment = '%s',
						tags = '%s'
				WHERE id = %d """ % (
						playlistobject.creator,
						int(playlistobject.fallback),
						playlistobject.title,
						playlistobject.description,
						playlistobject.comment,
						playlistobject.tags,
						playlistobject.id
				)
				#debug
				print updatestring
				cursor.execute(updatestring)

		def __deleteCompilationOwnersAndViewers(self, playlistid, cursor):
				"delete stuff related to this playlist in all tables"
				mediafiledeletionstring = """
				DELETE FROM compilation
				WHERE playlist = %d """ % playlistid

				ownerdeletionstring = """
				DELETE FROM playlistowners
				WHERE playlist = %d """ % playlistid

				viewerdeletionstring = """
				DELETE FROM playlistviewers
				WHERE playlist = %d """ % playlistid
		
				print mediafiledeletionstring
				cursor.execute(mediafiledeletionstring)
				print ownerdeletionstring
				cursor.execute(ownerdeletionstring)
				print viewerdeletionstring
				cursor.execute(viewerdeletionstring)
		
		def __getByCreator(self, creatorname, cursor):
				selectionstring = """
				SELECT  
						creator,
						fallback,
						title,
						description,
						comment,
						tags
				FROM playlists
				WHERE creator = '%s'""" % creatorname
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def insert(self, playlistobject):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						self.__insert(playlistobject, cursor)
						self.conn.commit()
						lastid = self.__getLastId(cursor)
						i = 0
						for mf in playlistobject.mediafilelist:
								self.__insertmediafile(lastid, mf.id, i, cursor)
								i+=1
						for uname in playlistobject.owners:
								self.__insertowner(lastid, uname, cursor)
						for uname in playlistobject.viewers:
								self.__insertviewer(lastid, uname, cursor)
						self.conn.commit()
						cursor.close()
						return lastid
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])
		
		def getById(self, playlistid):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getById(playlistid, cursor)

						#debug
						print "Number of playlist rows fetched: %d" % len(resultdicts)
						assert len(resultdicts) == 1
						#debug

						pl = PlayList(resultdicts[0])
						mediafiledao = MediaFileMysqlDAO(self.conn)

						resultdicts = self.__getMediaFiles(playlistid, cursor)
						for mfrow in resultdicts:
								mf = mediafiledao.getById(mfrow['mediafile'])
								pl.addMediaFile(mf)

						resultdicts = self.__getOwners(playlistid, cursor)
						for urow in resultdicts:
								pl.addOwner(urow['user'])

						resultdicts = self.__getViewers(playlistid, cursor)
						for urow in resultdicts:
								pl.addViewer(urow['user'])

						cursor.close()
						return pl
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def removeById(self, playlistid):
				try:
						cursor = self.conn.cursor()
						self.__removeById(playlistid, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of playlist rows deleted: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def update(self, playlistobject):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						self.__deleteCompilationOwnersAndViewers(playlistobject.id, cursor)
						self.conn.commit() #needed?
						self.__update(playlistobject, cursor)
						lastid = playlistobject.id
						i = 0
						for mf in playlistobject.mediafilelist:
								self.__insertmediafile(lastid, mf.id, i, cursor)
								i+=1
						for uname in playlistobject.owners:
								self.__insertowner(lastid, uname, cursor)
						for uname in playlistobject.viewers:
								self.__insertviewer(lastid, uname, cursor)
						self.conn.commit()
						cursor.close()
						return lastid
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])
		
		def getByCreator(self, creatorname):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						plresultdicts = self.__getByCreator(creatorname, cursor)

						#debug
						print "Number of playlist rows fetched: %d" % len(plresultdicts)
						#debug

						mediafiledao = MediaFileMysqlDAO(self.conn)
						res = []
						for plist in plresultdicts:
								pl = PlayList(plist)

								resultdicts = self.__getMediaFiles(pl.id, cursor)
								for mfrow in resultdicts:
										mf = mediafiledao.getById(mfrow['mediafile'])
										pl.addMediaFile(mf)

								resultdicts = self.__getOwners(pl.id, cursor)
								for urow in resultdicts:
										pl.addOwner(urow['user'])

								resultdicts = self.__getViewers(pl.id, cursor)
								for urow in resultdicts:
										pl.addViewer(urow['user'])

								res.append(pl)
						cursor.close()
						return res
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])


class TimeSlotMysqlDAO(RadioMateParentMysqlDAO):
		"The MySQL Database Access Object for radio show time slots"
		def __isGoodTimeSlot(self, timeslotobject, cursor):
				"check if the timeslotobject can be inserted in the radio's timetable"
				# time conflict conditions
				# +---+ = existing timeslot = (b+, e+)
				# *---* = new timeslot = (b*, e*)
				#
				#  b+         e+
				#  +----------+
				#       b*          e*
				#       *-----------*   b+ < b* < e+  but also  b* < e+ < e*
				#
				#
				#       b+          e+
				#       +-----------+ 
				#  b*        e*
				#  *---------*          b+ < e* < e+  but also  b* < b+ < e*
				# 
				# 
				#    b+        e+
				#    +---------+
				#  b*            e*
				#  *-------------*      b* < b+ < e*,  b* < e+ < e*  ---> first two cases together
				# 
				#  
				#   b+         e+
				#  +-------------+
				#    b*        e*
				#    *---------*        b+ < b* < e+,  b+ < e* < e+  ---> first two cases together
				# 
				# 
				selectionstring = """
				SELECT  
						id,
						creator, 
						beginningtime,
						endingtime,
						title
				FROM timeslots
				WHERE """
				# b+ < b* < e+
				selectionstring += "(beginningtime <= '%s' AND '%s' <= endingtime) OR \n" %\
								(timeslotobject.getBeginningDatetime(), timeslotobject.getBeginningDatetime())
				# b+ < e* < e+
				selectionstring += "(beginningtime <= '%s' AND '%s' <= endingtime) OR \n" %\
								(timeslotobject.getEndingDatetime(), timeslotobject.getEndingDatetime())
				# b* < b+ < e*
				selectionstring += "('%s' <= beginningtime AND beginningtime <= '%s') OR \n" %\
								(timeslotobject.getBeginningDatetime(), timeslotobject.getEndingDatetime())
				# b* < e+ < e*
				selectionstring += "('%s' <= endingtime AND endingtime <= '%s')" %\
								(timeslotobject.getBeginningDatetime(), timeslotobject.getEndingDatetime())

				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def __insert(self, timeslotobject, cursor):
				insertionstring = """
				INSERT INTO timeslots (
						creator, 
						slottype,
						beginningtime,
						endingtime,
						title,
						description,
						comment,
						tags,
						slotparameters,
						fallbackplaylist
				) VALUES (
				'%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', %d)""" % (
						timeslotobject.creator,
						timeslotobject.slottype,
						timeslotobject.getBeginningDatetime(),
						timeslotobject.getEndingDatetime(),
						timeslotobject.title,
						timeslotobject.description,
						timeslotobject.comment,
						timeslotobject.tags,
						json.dumps(timeslotobject.slotparams),
						timeslotobject.fallbackplaylist
				)
				#debug
				print insertionstring
				cursor.execute(insertionstring)

		def __getLastId(self, cursor):
				selectionstring = """
				SELECT LAST_INSERT_ID() AS lastid 
				"""
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()[0]['lastid']

		def __getById(self, timeslotid, cursor):
				selectionstring = """
				SELECT  
						id,
						creator, 
						slottype,
						beginningtime,
						endingtime,
						title,
						description,
						comment,
						slotparameters,
						fallbackplaylist,
						tags
				FROM timeslots
				WHERE id = %d""" % timeslotid
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def __removeById(self, timeslotid, cursor):
				deletionstring = """
				DELETE FROM timeslots
				WHERE id = %d""" % timeslotid
				#debug
				print deletionstring
				cursor.execute(deletionstring)
		
		def isGoodTimeSlot(self, timeslotobject):
				try:
						cursor = self.conn.cursor()
						resultdicts = self.__isGoodTimeSlot(timeslotobject, cursor)
						cursor.close()
						
						#debug
						print "Number of timeslot rows fetched: %d" % len(resultdicts)
						#debug

						if len(resultdicts) == 0:
								return True
						else:
								return False
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def insert(self, timeslotobject):
				try:
						if not self.isGoodTimeSlot(timeslotobject):
								raise RadioMateBadTimeSlotException()
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						self.__insert(timeslotobject, cursor)
						self.conn.commit()
						lastid = self.__getLastId(cursor)
						cursor.close()
						#debug
						print "Number of timeslot rows inserted: %d. Last id = %d" % (cursor.rowcount, lastid)
						return lastid
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])
		
		def getById(self, timeslotid):
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getById(timeslotid, cursor)
						cursor.close()

						#debug
						print "Number of timeslot rows fetched: %d" % len(resultdicts)
						assert len(resultdicts) == 1
						#debug

						rs = resultdicts[0]
						ts = TimeSlot()
						ts.id = rs['id']
						ts.creator = rs['creator']
						ts.slottype = rs['slottype']
						ts.title = rs['title']
						ts.description = rs['description']
						ts.comment = rs['comment']
						ts.tags = rs['tags']
						begintime = int(rs['beginningtime'])
						ts.beginningtime = begintime
						endtime = int(rs['endingtime'])
						ts.duration = (endtime - begintime)/60
						ts.slotparams = json.loads(rs['slotparameters'])
						ts.fallbackplaylist = rs['fallbackplaylist']
						return ts
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

		def removeById(self, timeslotid):
				try:
						cursor = self.conn.cursor()
						self.__removeById(timeslotid, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of timeslot rows deleted: %d" % cursor.rowcount
				except MySQLdb.Error, e:
						print "Error %d: %s" % (e.args[0], e.args[1])

if __name__ == '__main__':
		import json
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

		def mediafilesdaotest():
				mf = MediaFile()
				mf.user = "pippo2"
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
				mediafiledao = MediaFileMysqlDAO(conn)
				id = mediafiledao.insert(mf)
				mf2 = mediafiledao.getById(id)
				print mf2
				mediafiledao.removeById(id)
	
		def playlistdaotest():
				conn = MySQLdb.connect( 
								host = DBHOST, 
								user = DBUSER,
								passwd = DBPASSWORD,
								db = DATABASE
								)
				mf = MediaFile()
				mf.user = "pippo2"
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
				mf2.user = "pippo2"
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
				pl.creator = "pippo2"
				pl.fallback = False
				pl.description = "testing dao"
				pl.comment = ":)"
				pl.tags = "test,prova,foo,bar"

				pl.addMediaFile(mf)
				pl.addMediaFile(mf2)
				
				pl.addOwner("pippo")
				pl.addViewer("pippo2")

				print pl

				playlistdao = PlayListMysqlDAO(conn)
				plid = playlistdao.insert(pl)
				print plid
				pl2 = playlistdao.getById(plid)
				print pl2
				mediafiledao.removeById(id1)
				mediafiledao.removeById(id2)
				playlistdao.removeById(plid)
				conn.close()

		def timeslotdaotest():
				conn = MySQLdb.connect( 
								host = DBHOST, 
								user = DBUSER,
								passwd = DBPASSWORD,
								db = DATABASE
								)
				ts = TimeSlot()
				ts.creator = 'pippo'
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
				pl.creator = "pippo2"
				pl.fallback = False
				pl.description = "testing dao"
				pl.comment = ":)"
				pl.tags = "test,prova,foo,bar"
				playlistdao = PlayListMysqlDAO(conn)
				plid = playlistdao.insert(pl)

				ts.fallbackplaylist = plid

				tsdao = TimeSlotMysqlDAO(conn)
				tsid = tsdao.insert(ts)
				tsdao.removeById(tsid)
				playlistdao.removeById(plid)
				conn.close()
		#execute
		#mediafilesdaotest()
		#playlistdaotest()
		timeslotdaotest()

