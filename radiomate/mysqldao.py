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
from daobase import *

# The MySQL Data Access Objects

class MysqlConnectionManager(RadioMateConnectionManager):
		"given the right parameters connect to the database"
		def __init__(self, dbhost, dbuser, dbpassword, database):
				RadioMateConnectionManager.__init__(self, dbhost, dbuser, dbpassword, database)
				conn = MySQLdb.connect(
								host = self.dbhost, 
								user = self.dbuser, 
								passwd = self.dbpassword, 
								db = self.database
								)
				assert isinstance(conn, MySQLdb.connections.Connection)
				self.conn = conn

		def __del__(self):
				self.conn.close()

		def getMysqlConnection(self):
				return self.conn


class RadioMateParentMysqlDAO(object):
		"The parent class from which the other classess representing MySQL Database Access Objects (DAOs) inherit"
		def __init__(self, conn):
				if isinstance(conn, MysqlConnectionManager):
						self.connectionmanager = conn
						self.conn = self.connectionmanager.getMysqlConnection()
				elif isinstance(conn, MySQLdb.connections.Connection):
						self.conn = conn
				else:
						raise RadioMateDAOException("Invalid object for MySQL connection: %s", self.conn)


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
				"Create a new Role"
				try:
						cursor = self.conn.cursor()
						self.__insert(roleobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of role rows inserted: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)
		
		def getByName(self, rolename):
				"Get a Role from its name"
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getByName(rolename, cursor)
						cursor.close()

						#debug
						print "Number of role rows fetched: %d" % len(resultdicts)
						assert len(resultdicts) <= 1
						#debug

						if len(resultdicts) == 1:
								return Role(resultdicts[0])
						else:
								return None
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def removeByName(self, rolename):
				"Remove a Role from its name"
				try:
						cursor = self.conn.cursor()
						self.__removeByName(rolename, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of role rows deleted: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def getAll(self):
				"Get the list of all Roles"
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
						raise RadioMateDAOException(e.args)
		
		def update(self, roleobject):
				"Update an existing Role"
				try:
						cursor = self.conn.cursor()
						self.__update(roleobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of role rows updated: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)


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
				#TODO: passwords should NEVER leave the database!!!
				selectionstring = """
				SELECT  
						name,
						password,
						displayname,
						role
				FROM users
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
				"Insert a new user"
				try:
						cursor = self.conn.cursor()
						self.__insert(userobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of user rows inserted: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)
		
		def getByName(self, username):
				"Get an user from its username"
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getByName(username, cursor)
						cursor.close()

						#debug
						print "Number of user rows fetched: %d" % len(resultdicts)
						assert len(resultdicts) <= 1
						#debug

						if len(resultdicts) == 1:
								u = User(resultdicts[0])
								roledao = RoleMysqlDAO(self.conn)
								u.role = roledao.getByName(u.rolename)
								return u
						else:
								return None
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def removeByName(self, username):
				"Remove an user from its username"
				try:
						cursor = self.conn.cursor()
						self.__removeByName(username, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of user rows deleted: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def getAll(self):
				"Get the list of all users"
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
						raise RadioMateDAOException(e.args)

		def update(self, userobject):
				"Update an existing user"
				try:
						cursor = self.conn.cursor()
						self.__update(userobject, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of user rows updated: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)
		

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
				def whereand(n):
						if n == 0:
								return " WHERE "
						else:
								return " AND "
				i = 0
				if partialmediafile.user:
						searchstring += whereand(i) + " user LIKE '%%%s%%' " % partialmediafile.user
						i+=1
				if partialmediafile.path:
						searchstring += whereand(i) + " path LIKE '%%%s%%' " % partialmediafile.path
						i+=1
				if partialmediafile.title:
						searchstring += whereand(i) + " title LIKE '%%%s%%' " % partialmediafile.title
						i+=1
				if partialmediafile.author:
						searchstring += whereand(i) + " author LIKE '%%%s%%' " % partialmediafile.author
						i+=1
				if partialmediafile.album:
						searchstring += whereand(i) + " album LIKE '%%%s%%' " % partialmediafile.album
						i+=1
				if partialmediafile.genre:
						searchstring += whereand(i) + " genre LIKE '%%%s%%' " % partialmediafile.genre
						i+=1
				if partialmediafile.year:
						searchstring += whereand(i) + " year = %d " % partialmediafile.year
						i+=1
				if partialmediafile.comment:
						searchstring += whereand(i) + " comment LIKE '%%%s%%' " % partialmediafile.comment
						i+=1
				if partialmediafile.license:
						searchstring += whereand(i) + " license LIKE '%%%s%%' " % partialmediafile.license
						i+=1
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
						id = '%d'
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
				"Insert a new media file"
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
						raise RadioMateDAOException(e.args)
		
		def getById(self, mediafileid):
				"Get a media file from its id"
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
						raise RadioMateDAOException(e.args)

		def removeById(self, mediafileid):
				"Remove a media file from its id"
				try:
						cursor = self.conn.cursor()
						self.__removeById(mediafileid, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of mediafile rows deleted: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def search(self, partialmediafile):
				"Search for a media file"
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
						raise RadioMateDAOException(e.args)
		
		def update(self, mediafileobject):
				"Update an existing media file"
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						self.__update(mediafileobject, cursor)
						self.conn.commit()
						lastid = mediafileobject.id
						cursor.close()
						#debug
						print "Number of mediafile rows updated: %d. id = %d" % (cursor.rowcount, lastid)
						return lastid
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)


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
						id,
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
						id,
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
		
		def __getByUser(self, username, cursor):
				"Returns playlist ids in which the user is creator, owner or viewer"
				selectionstring = """
				SELECT  
						playlists.id
				FROM playlists JOIN (playlistowners, playlistviewers)
				ON (playlistowners.playlist = playlists.id AND playlistviewers.playlist = playlists.id)
				WHERE 
				playlists.creator = '%s' OR
				playlistowners.user = '%s' OR
				playlistviewers.user = '%s'
				""" % (username, username, username)
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()

		def insert(self, playlistobject):
				"Insert a new Playlist in the database"
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
						raise RadioMateDAOException(e.args)
		
		def getById(self, playlistid):
				"Get a Playlist from its id"
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
						raise RadioMateDAOException(e.args)

		def removeById(self, playlistid):
				"Remove a playlist from its id"
				try:
						cursor = self.conn.cursor()
						self.__removeById(playlistid, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of playlist rows deleted: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def update(self, playlistobject):
				"Update an existing playlist"
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
						raise RadioMateDAOException(e.args)
		
		def getByCreator(self, creatorname):
				"Get the playlists of a given creator"
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
						raise RadioMateDAOException(e.args)

		def getByUser(self, username):
				"Returns playlists in which the user is creator, owner or viewer"
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						plresultdicts = self.__getByUser(username, cursor)
						cursor.close()

						#debug
						print "Number of playlist rows fetched: %d" % len(plresultdicts)
						#debug
						res = []
						for plres in plresultdicts:
								assert len(plres) == 1
								plid = plres['id']
								pl = self.getById(plid)
								res.append(pl)
						return res
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)


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
		
		def __update(self, timeslotobject, cursor):
				updatestring = """
				UPDATE timeslots 
				SET 
						creator = '%s', 
						slottype = '%s',
						beginningtime = '%s',
						endingtime = '%s',
						title = '%s',
						description = '%s',
						comment = '%s',
						tags = '%s',
						slotparameters = '%s',
						fallbackplaylist = %d
				WHERE id = %d
				""" % (
						timeslotobject.creator,
						timeslotobject.slottype,
						timeslotobject.getBeginningDatetime(),
						timeslotobject.getEndingDatetime(),
						timeslotobject.title,
						timeslotobject.description,
						timeslotobject.comment,
						timeslotobject.tags,
						json.dumps(timeslotobject.slotparams),
						timeslotobject.fallbackplaylist,
						timeslotobject.id
				)
				#debug
				print updatestring
				cursor.execute(updatestring)
		
		def __getFromTo(self, fromdate, todate, cursor):
				"fromdate and todate are date+time strings"
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
				WHERE beginningtime >= '%s' AND beginningtime <= '%s'""" % (fromdate, todate)
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()
		
		def __search(self, timeslotobject, cursor):
				"Search for timeslots"
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
				"""

				def whereand(n):
						if n == 0:
								return " WHERE "
						else:
								return "OR"
				i = 0
				if timeslotobject.title:
						selectionstring += whereand(i) + " title LIKE '%%%s%%' " % timeslotobject.title
						i+=1
				if timeslotobject.description:
						selectionstring += whereand(i) + " description LIKE '%%%s%%' " % timeslotobject.description
						i+=1
				if timeslotobject.comment:
						selectionstring += whereand(i) + " comment LIKE '%%%s%%' " % timeslotobject.comment
						i+=1
				if timeslotobject.tags:
						selectionstring += whereand(i) + " tags LIKE '%%%s%%' " % timeslotobject.tags
						i+=1
				if timeslotobject.creator:
						selectionstring += whereand(i) + " creator = '%s'" % timeslotobject.creator
				#debug
				print selectionstring
				cursor.execute(selectionstring)
				return cursor.fetchall()
		
		def isGoodTimeSlot(self, timeslotobject):
				"Returns true iff the timeslot does not conflict with existing timeslots"
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__isGoodTimeSlot(timeslotobject, cursor)
						cursor.close()
						
						#debug
						print "Number of timeslot rows fetched: %d" % len(resultdicts)
						#debug

						if len(resultdicts) == 0:
								return True
						elif len(resultdicts) == 1:
								if int(resultdicts[0]['id']) == timeslotobject.id:
										return True
						else:
								return False
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def insert(self, timeslotobject):
				"Insert a new timeslot in the database"
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
						raise RadioMateDAOException(e.args)
		
		def getById(self, timeslotid):
				"Get a timeslot from its id"
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
						ts.setBeginningDateTime(rs['beginningtime'])
						ts.setEndingDateTime(rs['endingtime'])
						ts.slotparams = json.loads(rs['slotparameters'])
						ts.fallbackplaylist = rs['fallbackplaylist']
						return ts
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def removeById(self, timeslotid):
				"Remove a timeslot from its id"
				try:
						cursor = self.conn.cursor()
						self.__removeById(timeslotid, cursor)
						self.conn.commit()
						cursor.close()
						#debug
						print "Number of timeslot rows deleted: %d" % cursor.rowcount
						return cursor.rowcount
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def update(self, timeslotobject):
				"Update an existing timeslot"
				try:
						if not self.isGoodTimeSlot(timeslotobject):
								raise RadioMateBadTimeSlotException()
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						self.__update(timeslotobject, cursor)
						self.conn.commit()
						lastid = timeslotobject.id
						cursor.close()
						#debug
						print "Number of timeslot rows inserted: %d. Last id = %d" % (cursor.rowcount, lastid)
						return lastid
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)

		def getFromTo(self, fromdate, todate):
				"Get timeslots between fromdate and todate date+time strings"
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__getFromTo(fromdate, todate, cursor)
						cursor.close()

						#debug
						print "Number of timeslot rows fetched: %d" % len(resultdicts)
						#debug

						res = []
						for rs in resultdicts:
								ts = TimeSlot()
								ts.id = rs['id']
								ts.creator = rs['creator']
								ts.slottype = rs['slottype']
								ts.title = rs['title']
								ts.description = rs['description']
								ts.comment = rs['comment']
								ts.tags = rs['tags']
								ts.setBeginningDateTime(rs['beginningtime'])
								ts.setEndingDateTime(rs['endingtime'])
								ts.slotparams = json.loads(rs['slotparameters'])
								ts.fallbackplaylist = rs['fallbackplaylist']
								res.append(ts)
						return res
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)
		
		def search(self, timeslotobject):
				"Search for timeslots using the title, comment, description, tags and creator properties of timeslotobject"
				try:
						cursor = self.conn.cursor(MySQLdb.cursors.DictCursor)
						resultdicts = self.__search(timeslotobject, cursor)
						cursor.close()

						#debug
						print "Number of timeslot rows fetched: %d" % len(resultdicts)
						#debug

						res = []
						for rs in resultdicts:
								ts = TimeSlot()
								ts.id = rs['id']
								ts.creator = rs['creator']
								ts.slottype = rs['slottype']
								ts.title = rs['title']
								ts.description = rs['description']
								ts.comment = rs['comment']
								ts.tags = rs['tags']
								ts.setBeginningDateTime(rs['beginningtime'])
								ts.setEndingDateTime(rs['endingtime'])
								ts.slotparams = json.loads(rs['slotparameters'])
								ts.fallbackplaylist = rs['fallbackplaylist']
								res.append(ts)
						return res
				except MySQLdb.Error, e:
						raise RadioMateDAOException(e.args)



