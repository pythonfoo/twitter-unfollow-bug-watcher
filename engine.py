#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
import sys
import os
import config
import twython
import datetime
import collections

class engine(object):

	def __init__(self):
		self.version = '0.0.2'


		# tables
		self.tableFollowing = 'iFollow'
		self.tableUserInfo = 'userInfo'
		self.tableMissing = 'iMiss'
		self.tableSettings = 'settings'

		self.dbConnection = None
		self.dbCursor = None
		self.twitter = twython.Twython(app_key=config.TWITTER_CONSUMER_KEY,
										app_secret=config.TWITTER_CONSUMER_SECRET,
										oauth_token=config.TWITTER_ACCESS_TOKEN,
										oauth_token_secret=config.TWITTER_TOKEN_SECRET)

		if self.checkDb() == False:
			raise Exception('DB ERROR!')

		self.connectDb()

	def checkDb(self):
		# http://zetcode.com/db/sqlitepythontutorial/

		#  check if DB exist
		if not os.path.isfile(config.DB_NAME):
			print('Creating DB ' + config.DB_NAME + ' ...') #  create DB
			con = sqlite3.connect(config.DB_NAME)
			with con:
				cur = con.cursor()
				cur.execute('CREATE TABLE ' + self.tableFollowing + '(ID INTEGER PRIMARY KEY AUTOINCREMENT, userInfoId INT, firstSeenDate timestamp, lastSeenDate timestamp, deletedByMe INT)')
				con.commit()
				cur.execute('CREATE TABLE ' + self.tableUserInfo + '(ID INTEGER PRIMARY KEY AUTOINCREMENT, twitterId TEXT, name TEXT, screenName TEXT)')
				con.commit()
				cur.execute('CREATE TABLE ' + self.tableMissing + '(ID INTEGER PRIMARY KEY AUTOINCREMENT, userInfoId INT)')
				con.commit()
				cur.execute('CREATE TABLE ' + self.tableSettings + '(ID INTEGER PRIMARY KEY AUTOINCREMENT, property TEXT, value TEXT)')
				con.commit()

				cur.execute('INSERT INTO ' + self.tableSettings + " (property, value) VALUES(?, ?);", ('version', self.version))
				con.commit()
			con.close()

		#TODO: check DB!
		con = sqlite3.connect(config.DB_NAME)
		with con:
			cur = con.cursor()

			cur.execute('PRAGMA table_info(' + self.tableFollowing + ')')
			data = cur.fetchall()
			if not data:
				raise Exception(self.tableFollowing + ' DOES NOT EXIST!')

			cur.execute('PRAGMA table_info(' + self.tableUserInfo + ')')
			data = cur.fetchall()
			if not data:
				raise Exception(self.tableUserInfo + ' DOES NOT EXIST!')

			cur.execute('PRAGMA table_info(' + self.tableMissing + ')')
			data = cur.fetchall()
			if not data:
				raise Exception(self.tableMissing + ' DOES NOT EXIST!')

			cur.execute('PRAGMA table_info(' + self.tableSettings + ')')
			data = cur.fetchall()
			if not data:
				raise Exception(self.tableSettings + ' DOES NOT EXIST!')
		con.close()

		return True

	# not needed anymore!
	# sqlite3.Row
	#def dict_factory(cursor, row):
	#	d = {}
	#	for idx,col in enumerate(cursor.description):
	#		d[col[0]] = row[idx]
	#	return d

	def connectDb(self):
		self.dbConnection = sqlite3.connect(config.DB_NAME)
		self.dbConnection.row_factory = sqlite3.Row

		self.dbCursor = self.dbConnection.cursor()

		# configure
		self.dbConnection.text_factory = str

	def retrieveCurrentFollowing(self):
		ids = []
		cursor = -1
		while cursor != 0:
			apiData = self.twitter.get_friends_ids(cursor=cursor) #if group == 'followers' else twitter.get_friends_ids(cursor=cursor)
			#print 'retrieved (next): %s (%s)' % (len(apiData['ids']), apiData['next_cursor'])

			ids.extend(apiData['ids'])
			cursor = apiData['next_cursor']

		# fix L on end of IDS! like 2792649582L
		fixedIds = []
		for id in ids:
			fixedIds.append(str(id))
		return fixedIds

	def partition(self, alist, indices):
		return [alist[i:j] for i, j in zip([0]+indices, indices+[None])]

	def convertToUtf8(self, data):
		if isinstance(data, basestring):
			#return str(data)
			return data.encode('utf-8')
		elif isinstance(data, collections.Mapping):
			return dict(map(self.convertToUtf8, data.iteritems()))
		elif isinstance(data, collections.Iterable):
			return type(data)(map(self.convertToUtf8, data))
		else:
			return data

	def getDetailsForIds(self, ids):
		#newlist = [sublist[:2] for sublist in ids]
		newlist = self.partition(ids, range(0, len(ids), 100)[1:])
		#print newlist
		commitString = ''
		for partIds in newlist:
			user_ids_string = ','.join(map(str, partIds))
			#print user_ids_string
			apiData = []
			try:
				apiData = self.twitter.lookup_user(user_id=user_ids_string)
			except Exception as ex:
				print 'Cannot retrieve data for User %s' % user_ids_string
				print ex

			for user in apiData:
				#{u'follow_request_sent': False, u'profile_use_background_image': True, u'profile_text_color': u'333333', u'default_profile_image': False, u'id': 2792649582L, u'profile_background_image_url_https': u'https://abs.twimg.com/images/themes/theme14/bg.gif', u'verified': False, u'profile_location': None, u'profile_image_url_https': u'https://pbs.twimg.com/profile_images/515617762111000576/PYnTser9_normal.png', u'profile_sidebar_fill_color': u'DDEEF6', u'entities': {u'url': {u'urls': [{u'url': u'http://t.co/dRvUijIU01', u'indices': [0, 22], u'expanded_url': u'http://spacestationloma.com/', u'display_url': u'spacestationloma.com'}]}, u'description': {u'urls': []}}, u'followers_count': 1, u'profile_sidebar_border_color': u'000000', u'id_str': u'2792649582', u'profile_background_color': u'131516', u'listed_count': 0, u'status': {u'contributors': None, u'truncated': False, u'text': u'SPACE: The final fro... DAMN!\nits really busy out here http://t.co/ap8IOBFKyU', u'in_reply_to_status_id': None, u'id': 515618567216463873L, u'favorite_count': 0, u'source': u'<a href="http://twitter.com" rel="nofollow">Twitter Web Client</a>', u'retweeted': False, u'coordinates': None, u'entities': {u'symbols': [], u'user_mentions': [], u'hashtags': [], u'urls': [], u'media': [{u'expanded_url': u'http://twitter.com/SpaceStationL/status/515618567216463873/photo/1', u'display_url': u'pic.twitter.com/ap8IOBFKyU', u'url': u'http://t.co/ap8IOBFKyU', u'media_url_https': u'https://pbs.twimg.com/media/ByfYWn_CIAA5W89.png', u'id_str': u'515618565559296000', u'sizes': {u'large': {u'h': 682, u'resize': u'fit', u'w': 1024}, u'small': {u'h': 226, u'resize': u'fit', u'w': 340}, u'medium': {u'h': 399, u'resize': u'fit', u'w': 600}, u'thumb': {u'h': 150, u'resize': u'crop', u'w': 150}}, u'indices': [55, 77], u'type': u'photo', u'id': 515618565559296000L, u'media_url': u'http://pbs.twimg.com/media/ByfYWn_CIAA5W89.png'}]}, u'in_reply_to_screen_name': None, u'id_str': u'515618567216463873', u'retweet_count': 0, u'in_reply_to_user_id': None, u'favorited': False, u'geo': None, u'in_reply_to_user_id_str': None, u'possibly_sensitive': False, u'lang': u'en', u'created_at': u'Fri Sep 26 21:47:00 +0000 2014', u'in_reply_to_status_id_str': None, u'place': None}, u'is_translation_enabled': False, u'utc_offset': None, u'statuses_count': 3, u'description': u'SPAAACE... IM IN SPACE... A SPACE STATION... IN SPACE', u'friends_count': 1, u'location': u'Sector: LOMA', u'profile_link_color': u'ABB8C2', u'profile_image_url': u'http://pbs.twimg.com/profile_images/515617762111000576/PYnTser9_normal.png', u'following': True, u'geo_enabled': False, u'profile_banner_url': u'https://pbs.twimg.com/profile_banners/2792649582/1411767336', u'profile_background_image_url': u'http://abs.twimg.com/images/themes/theme14/bg.gif', u'name': u'SpaceStation: Loma', u'lang': u'de', u'profile_background_tile': True, u'favourites_count': 2, u'screen_name': u'SpaceStationL', u'notifications': False, u'url': u'http://t.co/dRvUijIU01', u'created_at': u'Fri Sep 05 22:08:27 +0000 2014', u'contributors_enabled': False, u'time_zone': None, u'protected': False, u'default_profile': False, u'is_translator': False}
				user = self.convertToUtf8(user)
				#print user
				#print 'NEW USER: {} | {} | {}'.format(user['id'], user['name'], user['screen_name'])
				#print 'https://twitter.com/%s' % user['screen_name']
				#print user['description']
				#print ''

				#commitString += 'INSERT INTO ' + self.tableUserInfo + " VALUES(6,'Citroen',21000);".format()
				#commitString += 'INSERT INTO ' + self.tableFollowing + " VALUES(6,'Citroen',21000);"
				# twitterId TEXT, name TEXT, nameLabel
				qry = 'INSERT INTO ' + self.tableUserInfo + " (twitterId, name, screenName) VALUES(?, ?, ?);" #.format(user['id'], user['name'], user['screen_name'])
				self.dbCursor.execute(qry, (user['id'], user['name'], user['screen_name']))
				lastId = self.dbCursor.lastrowid
				now = datetime.datetime.now()
				# userInfoId INT, firstSeenDate INT, lastSeenDate INT, deletedByMe INT
				#self.dbCursor.execute('INSERT INTO ' + self.tableFollowing + " (userInfoId, firstSeenDate, lastSeenDate, deletedByMe) VALUES({},'{}','{}',{});".format(
				#																lastId, now, now, -1))
				self.dbCursor.execute('INSERT INTO ' + self.tableFollowing + " (userInfoId, firstSeenDate, lastSeenDate, deletedByMe) VALUES(?, ?, ?, ?);", (lastId, now, now, -1))

		#INSERT INTO Cars VALUES(6,'Citroen',21000);
		self.dbCursor.execute(commitString)
		self.dbConnection.commit()

	def getFollowingFromDb(self):
		self.dbCursor.execute('SELECT * FROM ' + self.tableFollowing + ' JOIN ' + self.tableUserInfo + ' ON ' + self.tableFollowing + '.userInfoId=' + self.tableUserInfo + '.ID WHERE deletedByMe!=1')
		rows = self.dbCursor.fetchall()

		return rows

	def setMarkAs(self, mode):
		self.dbCursor.execute('SELECT * FROM ' + self.tableMissing)
		rows = self.dbCursor.fetchall()

		for row in rows:
			self.dbCursor.execute('UPDATE ' + self.tableFollowing + ' SET deletedByMe=? WHERE ID=?', (mode, row['userInfoId']))
			self.dbConnection.commit()
			print 'set ' + str(row['userInfoId']) + ' to ' + str(mode)


	def doCheck(self):
		currentFollowing = self.retrieveCurrentFollowing()
		#self.getDetailsForIds(currentFollower)
		lastFollowing = self.getFollowingFromDb()
		print 12*'*'
		print 'currentFollowing:', len(currentFollowing)
		print 'lastFollowing:', len(lastFollowing)
		print 12*'*'

		# SYNC!
		foundIds = []
		notFoundIds = []
		for followingUserInfo in lastFollowing:
			if followingUserInfo['twitterId'] in currentFollowing:
				#print 'FOUND: ' + followingUserInfo['twitterId'] + ' NAME: ' + followingUserInfo['name']
				foundIds.append(followingUserInfo['twitterId'])
			else:
				#print 'unknown user: ' + followingUserInfo['twitterId']
				notFoundIds.append(followingUserInfo['twitterId'])

		needInfosForIds = []
		for twitterId in currentFollowing:
			if twitterId in notFoundIds or not twitterId in foundIds:
				# this is a new user!
				needInfosForIds.append(twitterId)

		if len(needInfosForIds) > 0:
			self.getDetailsForIds(needInfosForIds)

		# after synchronisation, check again
		#lastFollowingDict = {}
		#for user in self.getFollowingFromDb():
		#	lastFollowingDict[user['twitterId']] = user
		notFoundIds = []
		for user in lastFollowing:
			if not user['twitterId'] in currentFollowing:
				notFoundIds.append(user['ID'])
				print 'you lost one| ID: "{}" | name: "{}" | screen name: "{}"'.format(user['ID'], user['name'], user['screenName'])

		self.dbCursor.execute('DELETE FROM ' + self.tableMissing)
		self.dbCursor.execute('VACUUM')
		self.dbConnection.commit()

		if len(notFoundIds) > 1:
			self.dbCursor.executemany('INSERT INTO ' + self.tableMissing + ' (userInfoId) VALUES(?)', notFoundIds)
		elif len(notFoundIds) == 1:
			self.dbCursor.execute('INSERT INTO ' + self.tableMissing + ' (userInfoId) VALUES(?)', (notFoundIds[0],))
		self.dbConnection.commit()

if __name__ == '__main__':
	eng = engine()
	eng.doCheck()