from flask import Flask, render_template, request, make_response, redirect, flash
import bcrypt
import mysql.connector
import hashlib
from utilities import *
import uuid
mydb = mysql.connector.connect(host = "localhost", user = "root", password = "iloveelephantsmalls", database = "credentials")
app=Flask(__name__)
@app.route('/', methods = ["POST", "GET"])
def home():
    cursor = mydb.cursor()

    #If an authToken is set in cookies -> A user is logged in.
    if "authToken" in request.cookies:
        authToken = request.cookies["authToken"]

        #Hash the authToken cookie.
        hashedToken = hashlib.sha256()
        hashedToken.update(bytes.fromhex(authToken))
        hashedToken = hashedToken.hexdigest()

        #Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken ='" + hashedToken + "'"
        cursor.execute(statement)
        result = cursor.fetchall()

        if(len(result) == 1):
            record = result[0][0]

            #body: homeLoggedIn.html with username injected to be served in response.
            body = createHomePage(record)

            #Make and return the home page response.
            response = make_response()
            response.data = body.encode('utf-8')
            response.content_type = "text/html; charset=utf-8"
            response.content_length = len(body.encode('utf-8'))
            return response

    #If there is no authToken -> No user is logged in.
    return render_template("home.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registerForm", methods = {"POST"})
def registerForm():
    #Create base redirect response.
    response = make_response(redirect("/", code = 302))

    #cursor: To interact with database.
    cursor = mydb.cursor()

    #Create logins table.
    statement = "CREATE TABLE IF NOT EXISTS logins(username VARCHAR(255), hashedPass VARCHAR(255))"
    cursor.execute(statement)

    #Create authTokens table if it doesn't exist.
    cursor = mydb.cursor()
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Parse username, password, and reentered password.
    username = request.form.get('username')
    password = request.form.get('password')
    repassword = request.form.get('repassword')

    #Find login for input username.
    statement = "SELECT * FROM logins WHERE username ='" + username + "'"
    cursor.execute(statement)
    result = cursor.fetchall()

    #Computes how many instances are associated with that username: should be either 0 or 1.
    exists = 0
    for element in result:
        exists += 1

    #If there is not a registered user with the username:
    if exists == 0:

        #Check if the passwords matched for verification.
        if (password == repassword):

            #Salt + hash password.
            salt = bcrypt.gensalt()
            hashPass = bcrypt.hashpw(password.encode('utf-8'), salt)
            stringHash = hashPass.decode('utf-8')


            #Stored salted + hashed password in database, along with the username.
            statement = "INSERT INTO logins(username, hashedPass) VALUES (%s, %s)"
            values = (username, stringHash)
            cursor.execute(statement, values)

            #Generate authToken for user.
            generateAuthToken(username, cursor, response)

            # Save changes to database.
            mydb.commit()

            return response

        #If password & repassword don't match, return register form.
        else:
            print("Passwords don't match")
            return render_template("register.html")

    #If the usernane is already taken, return register form.
    else:
        print("Username is already taken!")
        return render_template("register.html")



@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loginForm", methods = {"POST"})
def loginForm():

    #Create base redirect response.
    response = make_response(redirect("/", code = 302))

    #Create authTokens table if it doesn't exist.
    cursor = mydb.cursor()
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Parse input username and password.
    username = request.form.get('username')
    password = request.form.get('password')


    #Find record of given username in database.
    statement = "SELECT hashedPass FROM logins WHERE username ='" + username + "'"
    cursor.execute(statement)
    result = cursor.fetchall()
    record = result[0][0]

    #Verify the given password and stored password.
    valid = bcrypt.checkpw(password.encode('utf-8'), record.encode('utf-8'))

    mydb.commit()

    #If passwords match, authenticate user.
    if valid == True:

        #Generate authToken for user.
        generateAuthToken(username, cursor, response)

        #Create homeLoggedIn.html with injected username for response.
        createHomePage(username)

        return response

    #If the passwords do not match, don't authenticate.
    else:
        flash("Invalid username/password.")
        return render_template("login.html")


@app.route("/logout")
def logOut():
    cursor = mydb.cursor()

    #Take authToken from cookies.
    authToken = request.cookies["authToken"]

    #Hash authentication token.
    hashedToken = hashlib.sha256()
    hashedToken.update(bytes.fromhex(authToken))
    hashedToken = hashedToken.hexdigest()

    #Delete token from authTokens table.
    statement = "DELETE FROM authTokens WHERE hashedToken='" + hashedToken+"'"
    cursor.execute(statement)

    #Redirect to home page.
    return redirect("/", code = 302)

@app.route("/elephant-maker")
def elephantMaker():
    return render_template("elephant-maker.html")

#Elephants are saved in the form:
#[('title', '<title>'), ('file', '<submitted elephants url>')]
@app.route("/save-elephant", methods=["POST"])
def save_elephant():
    print("Form: ",request.form)
    #Save form data to SQL database

    #....Add Here....

    #Redirect back to the elephant maker page
    return render_template("elephant-maker.html")

#Elephants are submitted in the form:
#[('title', '<title>'), ('event', <'event name'>), ('file', '<submitted elephants url>')]
@app.route("/submit-elephant", methods=["POST"])
def submit_elephant():
    print("Form: ",request.form)
    #Save form data to SQL database

    #....Add Here....

    #Redirect back to the elephant maker page
    return render_template("elephant-maker.html")

@app.route("/elephant-feed")
def elephantFeed():
    return render_template("elephant-feed.html")

if __name__=='__main__':
    app.run(host="localhost",port=8080)