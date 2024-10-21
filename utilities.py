from flask import Flask, render_template, request, make_response, redirect, flash
import bcrypt
import mysql.connector
import hashlib
from utilities import *
import uuid
mydb = mysql.connector.connect(host = "localhost", user = "root", password = "iloveelephantsmalls", database = "credentials")


#Create a string body for a response: Serve the homeLoggedIn.html with the param -> username.
def createHomePage(username):
    #Read homeLoggedIn.html template.
    with open("templates/homeLoggedIn.html", "r") as file:
        f = file.read()

        #Inject username.
        editUsername = f.split('<div class="item" id="header-user">{username}</div>')
        fileVer1 = editUsername[0] + '<div class="item" id="header-user">' + username + '</div>' + editUsername[1]
        return fileVer1

#Generate and store authentication token for user.
def generateAuthToken(username, cursor, response):
    #Generate uuid -> authentication token.
    unhashedAuthToken = uuid.uuid4().bytes

    #Hash authentication token.
    hashedToken = hashlib.sha256()
    hashedToken.update(unhashedAuthToken)
    hashedToken = hashedToken.hexdigest()

    #Insert token into authTokens table.
    statement = "INSERT INTO authTokens(username,hashedToken) VALUES (%s, %s)"
    values = (username, hashedToken)
    cursor.execute(statement, values)

    #Commit.
    mydb.commit()

    #Create authToken cookie to store unhashed authToken.
    response.set_cookie("authToken", unhashedAuthToken.hex(), httponly=True, max_age=7200)
