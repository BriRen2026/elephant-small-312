from flask import Flask, render_template, request, make_response, redirect, flash
import bcrypt
import mysql.connector
import hashlib
import uuid

# Create credentials database if it doesn't exist at startup.
def createDatabase():
        #Connect to mysql server.
        myServer = mysql.connector.connect(host = 'mysql', user='root', password='iloveelephantsmalls')

        #Create cursor to execute statements.
        serverCursor = myServer.cursor()

        #Create database: credentials -> To store all information.
        serverCursor.execute(f"CREATE DATABASE IF NOT EXISTS {'credentials'}")

        #Connect to credentials database + create database cursor.
        myDB = mysql.connector.connect(host = 'mysql', user='root', password='iloveelephantsmalls', database = 'credentials')
        dbCursor = myDB.cursor()

        #Create table: authTokens -> To store usernames associated with hashed authentication tokens during user sessions.
        statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
        dbCursor.execute(statement)

        #Create table: logins -> To store usernames associated with hashed + salted passwords during registration.
        statement = "CREATE TABLE IF NOT EXISTS logins(username VARCHAR(255), hashedPass VARCHAR(255), profilePicture VARCHAR(255))"
        dbCursor.execute(statement)

        #Create table: posts -> To store elephant posts associated with information during elephant submission.
        statement = "CREATE TABLE IF NOT EXISTS posts(username VARCHAR(255), title VARCHAR(255),description VARCHAR(255), filePath VARCHAR(255), event VARCHAR(255), id VARCHAR(255), likes INT)"
        dbCursor.execute(statement)

        #added by zane, DB that contains username and post's div ID
        #Created table: likes -> To store usernames associated with post's div ID.
        statement = "CREATE TABLE IF NOT EXISTS likes(username VARCHAR(255), postID VARCHAR(255))"
        dbCursor.execute(statement)

        #For documentation purposes, Jenna has also made 2 tables (but it happens in submit elephant)
        #Because SQL CANNOT store lists, its best to have tables created associated with a SPECIFIC post to store data for that specific post

        #DB titled {postId}Comments which contains all comments and commenter usernames associated with a postID
        #Created table: {postID}Comments(username VARCHAR(255), comment VARCHAR(255))
        statement = "CREATE TABLE IF NOT EXISTS comments(username VARCHAR(255), postID VARCHAR(255), comment VARCHAR(255))"
        dbCursor.execute(statement)


        #Commit to server and database connections.
        myDB.commit()
        myServer.commit()


        #Close server and database cursors.
        dbCursor.close()
        serverCursor.close()


        #Close server and database connections.
        myServer.close()
        myDB.close()

# Create the database on app startup.
createDatabase()

mydb = mysql.connector.connect(host = "mysql", user = "root", password = "iloveelephantsmalls", database = "credentials")

#Create a string body for a response: Serve the homeLoggedIn.html with the username injected.
def createHomePage(username, pfp):
    #Read homeLoggedIn.html template.
    with open("templates/homeLoggedIn.html", "r") as file:
        f = file.read()

        #Inject username.
        #vvvv old code in case what i did was secretly horrifically wrong vvvv
        #editUsername = f.split('<div class="item" id="header-user">{username}</div>')
        #fileVer1 = editUsername[0] + '<div class="item" id="header-user">' + username + '</div>' + editUsername[1]
        fileVer1 = f.replace("{username}", username)
        fileVer1 = fileVer1.replace("{{pfp}}", pfp)

        return fileVer1

#Create a string body for a response: Serve the homeLoggedIn.html with the param -> username.
def createMakerPage(username, pfp):
    #Read homeLoggedIn.html template.
    with open("templates/elephant-maker.html", "r") as file:
        f = file.read()

        #Inject username.
        editUsername = f.split('{username}')
        fileVer1 = editUsername[0]
        editUsername.pop(0)

        #For every division in editUsername after split, insert the username.
        for section in editUsername:
            fileVer1 = fileVer1 + username + section

        fileVer1 = fileVer1.replace("{{pfp}}", pfp)

        return fileVer1

#Create a string body for a response: Serve the homeLoggedIn.html with the param -> username.
def createFeedPage(username, pfp):
    #Read homeLoggedIn.html template.
    with open("templates/elephant-feed.html", "r") as file:
        f = file.read()

        #Inject username.
        editUsername = f.split('{username}')
        fileVer1 = editUsername[0]
        editUsername.pop(0)

        for section in editUsername:
            fileVer1 = fileVer1 + username + section

        fileVer1 = fileVer1.replace("{{pfp}}", pfp)

        return fileVer1

def createProfilePage(username, pfp):
    # Read profile.html template
    with open("templates/profile.html", "r") as file:
        f = file.read()

        f = f.replace('{username}', username)
        f = f.replace('{{pfp}}', pfp)

        return f

#Generate and store authentication token for user.
def generateAuthToken(username, cursor, response, mydb):
    #Generate uuid -> authentication token.
    unhashedAuthToken = str(uuid.uuid4()).encode()
    hashedToken=hashlib.sha256(unhashedAuthToken).hexdigest()


    #Hash authentication token.
    # hashedToken = hashlib.sha256()
    # hashedToken.update(unhashedAuthToken)
    # hashedToken = hashedToken.hexdigest()

    #Insert token into authTokens table.
    statement = "INSERT INTO authTokens(username,hashedToken) VALUES (%s, %s)"
    values = (username, hashedToken)
    cursor.execute(statement, values)

    #Find username associated with authToken
    #statement = "SELECT * FROM authTokens"
    #cursor.execute(statement)
    #result = cursor.fetchall()
    #print (result)
    #print(len(result))

    #Commit to db.
    mydb.commit()

    #Create authToken cookie to store unhashed authToken.
    response.set_cookie("authToken", unhashedAuthToken.decode(), httponly=True, max_age=7200)

def getUser(request, mydb):
    #Create cursor.
    cursor = mydb.cursor(prepared=True)

    if 'authToken' in request.cookies:
        #Grab authToken.
        authToken = request.cookies["authToken"]

        #Hash the authToken cookie.
        hashedToken = hashlib.sha256(authToken.encode()).hexdigest()
        # hashedToken = hashlib.sha256()
        # hashedToken.update(bytes.fromhex(authToken))
        # hashedToken = hashedToken.hexdigest()

        #Find username associated with authToken
        #statement = "SELECT * FROM authTokens"
        #cursor.execute(statement)
        #print(cursor.fetchall())

        #Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
        t = hashedToken
        cursor.execute(statement, (t,))
        result = cursor.fetchall()

        #If there is a token associated with the username, serve the username.
        if (len(result) == 1):
            record = result[0][0]
            return record

        else:
            return "null"
    else:
        return "null"
