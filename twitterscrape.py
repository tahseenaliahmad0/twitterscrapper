# -*- coding: utf-8 -*-
import sys
import os
import tweepy
import mysql.connector
import regex as re
from datetime import date
from graphmaker import createGraph, createTable

#api authentication
consumer_key='I55MKpy2K9bvbYNbDh2Mq7YPu'
consumer_secret='ktJawewCfuWelRm4GBY4o9RG5au23KzjHrfp8wA6LV8mJj8PEn'
access_token='1102329177758486529-jezBOXW9AF5juCI4usKkYwKmtMH8DS'
access_token_secret='kHCa4NkgPkU2uQ1pkUyCoT6JrmG3eY7av67lbJn4rfjlw'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth,wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

#mySQL server
userdb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
)

#create cursor to execute mySQL 
cursor = userdb.cursor(buffered=True)

#CREATE a new database 'userdb' if no databse exists
cursor.execute("CREATE DATABASE IF NOT EXISTS usersdb")
cursor.execute("USE usersdb")

#set text encoding
cursor.execute('SET NAMES utf8mb4')
cursor.execute("SET CHARACTER SET utf8mb4")
cursor.execute("SET character_set_connection=utf8mb4")

#keywords to search for
keywords=input("enter keywords seperated by commas and NO spaces:")
keywords = keywords.split (",")
print("keywords: ", keywords)

#check day
today = date.today()
checkDate = today.strftime("%m-%d")



for keyword in keywords:

	print('creating tables for {key}'.format(key=(keyword)))
	#remove special characters from keyword to create table name
	tableName=re.sub('[^A-Za-z0-9]+', '', keyword)

	#create a new table for the keyword if none exist
	keywordTable = """CREATE TABLE IF NOT EXISTS {key} 
				 (id VARCHAR(20) PRIMARY KEY,
					username VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci, 
					bio VARCHAR(300) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
					location VARCHAR(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
					followers INT,
					following INT,
					isNew BOOLEAN
					)
					""".format(key=(tableName))
	cursor.execute(keywordTable)

	#create table to track occurance History
	historyTable="""CREATE TABLE IF NOT EXISTS {key} 
				   (checknum INT PRIMARY KEY AUTO_INCREMENT,
					checkDate VARCHAR(5) , 
					foundTotal INT,
					foundNew INT
					)
					""".format(key=(tableName + '_history'))
	cursor.execute(historyTable)

	#set all users to old
	setOld = """UPDATE {key} SET isNEW = false""".format(key=(tableName))
	cursor.execute(setOld)

	#store current users to compare with new users
	currentUsers = "SELECT id FROM {key}".format(key=(tableName))
	cursor.execute(currentUsers)
	oldUsers = cursor.fetchall()

	#mySQL code for inserting data into a table
	tableInsert = """INSERT INTO {key} (id, username, bio, location, followers, following, isNEW) 
					VALUES (%s,%s,%s,%s,%s,%s,%s)					""".format(key=(tableName))

	try:
		#fetch all users with keyword in description
		print('searching for users')
		matches=api.search_users(q=str(keyword),cout=100)

		#insert all relavent data into table
		for user in matches:
			id = user.id_str 
			name = user.name
			bio = user.description
			location= user.location
			followers = user.followers_count
			following = user.friends_count

			try:
				cursor.execute(tableInsert,(id,name,bio,location,followers,following,True))
				print('added user '+user.name)
			except mysql.connector.Error:
				print('user ' + user.name+' already added')
		#api error handling
	except tweepy.TweepError as e:
		print("error : " + str(e))
		break


	#save changes made to database
	userdb.commit()
	print("saving changes...")

	#check for changes in users
	if oldUsers!=None:
		cursor.execute(currentUsers)
		newUsers=cursor.fetchall()
		changes = list(set(newUsers)-set(oldUsers))
		print(str(len(changes)) + ' new users to ' + tableName)
	else:
		usersFound=cursor.execute("SELECT COUNT(id) FROM {key}".format(key=tableName))
		print('table '+tableName + ' created with ' + str(usersFound) + ' users')

	#update history
	foundTotal = len(newUsers)
	foundNew = len(changes)
	updateHistory="""INSERT INTO {key} (checkDate, foundTotal, foundNew) 
					VALUES (%s,%s,%s)					""".format(key=(tableName+ '_history'))
	cursor.execute(updateHistory,(checkDate, foundTotal, foundNew))

	userdb.commit()
	print("saving changes...again")

	print('creating '+ keyword + ' graph and table...')
	#get  data
	username = """SELECT username FROM {key}""".format(key=(tableName))
	cursor.execute(username)
	username = [''.join(i) for i in cursor.fetchall()] 

	bio = """SELECT bio FROM {key}""".format(key=(tableName))
	cursor.execute(bio)
	bio = [''.join(i) for i in cursor.fetchall()]

	location = """SELECT location FROM {key}""".format(key=(tableName))
	cursor.execute(location)
	location = [''.join(i) for i in cursor.fetchall()]

	followers = """SELECT followers FROM {key}""".format(key=(tableName))
	cursor.execute(followers)
	followers = [''.join(str(i[0])) for i in cursor.fetchall()]

	following = """SELECT following FROM {key}""".format(key=(tableName))
	cursor.execute(following)
	following = [''.join(str(i[0])) for i in cursor.fetchall()]

	isNew = """SELECT isNew FROM {key}""".format(key=(tableName))
	cursor.execute(isNew)
	isNew = cursor.fetchall()



	totalNum = """SELECT foundTotal FROM {key}""".format(key=(tableName+'_history'))
	cursor.execute(totalNum)
	totalNum =  list(map(int, [''.join(str(i[0])) for i in cursor.fetchall()]))

	newNum = """SELECT foundNew FROM {key}""".format(key=(tableName+'_history'))
	cursor.execute(newNum)
	newNum = list(map(int, [''.join(str(i[0])) for i in cursor.fetchall()]))

	checkNum = """SELECT COUNT(*) FROM {key}""".format(key=(tableName+'_history'))
	cursor.execute(checkNum)
	checkNum = cursor.fetchall()
	#create new graph and table for keyword
	
	createTable(keyword, username, bio, location, followers, following, isNew)
	createGraph(keyword, totalNum, newNum, checkNum)

#disconnect from mysql server
cursor.close()
if (userdb.is_connected()):
	userdb.close()
	print("mySQL connection is closed")



#access token : 1102329177758486529-jezBOXW9AF5juCI4usKkYwKmtMH8DS
#access token secret : kHCa4NkgPkU2uQ1pkUyCoT6JrmG3eY7av67lbJn4rfjlw