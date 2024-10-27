import json
from flask import Flask, render_template, request, make_response, redirect, flash
import mysql.connector
import hashlib
from utilities import *
import uuid
from markupsafe import Markup

app=Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "elephantsmalls"

@app.after_request #Sets the nosniff header on each responses
def add_security(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

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
        statement = "CREATE TABLE IF NOT EXISTS logins(username VARCHAR(255), hashedPass VARCHAR(255))"
        dbCursor.execute(statement)

        #Create table: posts -> To store elephant posts associated with information during elephant submission.
        statement = "CREATE TABLE IF NOT EXISTS posts(username VARCHAR(255), title VARCHAR(255),description VARCHAR(255), filePath VARCHAR(255), event VARCHAR(255), id VARCHAR(255), likes INT)"
        dbCursor.execute(statement)


        #added by zane, DB that contains username and post's div ID
        #Created table: likes -> To store usernames associated with post's div ID.
        statement = "CREATE TABLE IF NOT EXISTS likes(username VARCHAR(255), postID VARCHAR(255))"
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

#Connect to database: credentials.
mydb = mysql.connector.connect(host = "mysql", user = "root", password = "iloveelephantsmalls", database = "credentials")

@app.route('/', methods = ["POST", "GET"])
def home():

    #Create prepared database cursor for statement executions.
    cursor = mydb.cursor(prepared=True)

    #statement = "DELETE FROM authTokens"
    #cursor.execute(statement)
    #mydb.commit()

    #statement = "SELECT * FROM authTokens"
    #cursor.execute(statement)
    #print(cursor.fetchall())


    #If an authToken is set in cookies -> A user is logged in.
    if "authToken" in request.cookies:

        #Grab authToken from cookies.
        authToken = request.cookies["authToken"]

        #Hash the authToken cookie.
        hashedToken = hashlib.sha256()
        hashedToken.update(bytes.fromhex(authToken))
        hashedToken = hashedToken.hexdigest()

        #Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
        t = hashedToken
        cursor.execute(statement, (t,))
        result = cursor.fetchall()

        #If there is only one authentication token for the user.
        if(len(result) == 1):

            #Grab username from record in authTokens.
            record = result[0][0]

            #Create body: homeLoggedIn.html with username injected to be served in response.
            body = createHomePage(record)

            #Make and return the home page response.
            response = make_response()
            response.data = body.encode('utf-8')
            response.content_type = "text/html; charset=utf-8"
            response.content_length = len(body.encode('utf-8'))
            cursor.close()
            return response

        #If there is more than one authentication token for the user: invalid login.
        else:
            cursor.close()
            return render_template("home.html")

    #If there is no authToken -> No user is logged in.
    cursor.close()
    return render_template("home.html")


@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/registerForm", methods = {"POST"})
def registerForm():
    #Create base redirect response.
    response = make_response(redirect("/", code = 302))

    #Create prepared cursor: To interact with database.
    cursor = mydb.cursor(prepared=True)

    #Create logins table if it doesn't exist (for precautions).
    statement = "CREATE TABLE IF NOT EXISTS logins(username VARCHAR(255), hashedPass VARCHAR(255))"
    cursor.execute(statement)

    #Create authTokens table if it doesn't exist (for precautions).
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Parse username, password, and reentered password from form.
    username = request.form.get('username')
    password = request.form.get('password')
    repassword = request.form.get('repassword')

    #Find potential login for input username.
    statement = "SELECT * FROM logins WHERE username = %s"
    u=username
    cursor.execute(statement,(u,))
    result = cursor.fetchall()

    #Computes how many instances are associated with that username: should be either 0 or 1.
    #exists = 0
    #for element in result:
        #exists += 1

    #If there is not a registered user with the username:
    if len(result) == 0:

        #Check if the passwords matched for verification.
        #to be done: implement password validator
        #Stubbed out with [and True] for now for ease of testing. To be implemented for final demo.
        if (password == repassword and True):

            #Salt + hash password.
            salt = bcrypt.gensalt()
            hashPass = bcrypt.hashpw(password.encode('utf-8'), salt)
            stringHash = hashPass.decode('utf-8')


            #Stored salted + hashed password in database, along with the username.
            statement = "INSERT INTO logins(username, hashedPass) VALUES (%s, %s)"
            values = (username, stringHash)
            cursor.execute(statement, values)

            #Generate authToken for user.
            generateAuthToken(username, cursor, response, mydb)

            #Save changes to database.
            mydb.commit()

            cursor.close()
            return response

        #If password & repassword don't match, or password is not strong enough, return register form.
        else:
            print("Passwords don't match!")
            cursor.close()
            return render_template("register.html")

    #If the usernane is already taken, return register form.
    else:
        print("Username is already taken!")
        cursor.close()
        return render_template("register.html")


def validate_password(pwd):
    if len(pwd)<8:
        return False
    all_special = "!@#$%^&()-_="
    lower=False
    upper=False
    number=False
    special=False
    for char in pwd:
        if (not char.isalnum()) and (char not in all_special):
            return False
        if char.islower():
            lower=True
        if char.isupper():
            upper=True
        if char.isdigit():
            number=True
        if char in all_special:
            special=True
    if (not lower) or (not upper) or (not number) or (not special):
        return False
    return True


@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/loginForm", methods = {"POST"})
def loginForm():

    #Create base redirect response.
    response = make_response(redirect("/", code = 302))

    #Create authTokens table if it doesn't exist.
    cursor = mydb.cursor(prepared=True)
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Parse input username and password.
    username = request.form.get('username')
    password = request.form.get('password')

    #Find record of given username in database.
    statement = "SELECT hashedPass FROM logins WHERE username = %s"
    u=username
    cursor.execute(statement,(u,))
    result = cursor.fetchall()

    #If not registered.
    if (len(result) == 0):
        flash("Invalid username/password.")
        return render_template("login.html")

    #If registered.

    #Grab username.
    record = result[0][0]

    #Verify the given password and stored password.
    valid = bcrypt.checkpw(password.encode('utf-8'), record.encode('utf-8'))

    #Commit for good measure.
    mydb.commit()

    #If passwords match, authenticate user.
    if valid == True:

        #Generate authToken for user.
        generateAuthToken(username, cursor, response, mydb)

        #Create homeLoggedIn.html with injected username for response.
        createHomePage(username)

        #Commit.
        mydb.commit()

        cursor.close()
        return response

    #If the passwords do not match, don't authenticate.
    else:
        flash("Invalid username/password.")
        mydb.commit()
        cursor.close()
        return render_template("login.html")


@app.route("/logout")
def logOut():

    #Create cursor.
    cursor = mydb.cursor()

    #Create authTokens table if it doesn't exist.
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Take authToken from cookies.
    authToken = request.cookies["authToken"]

    #Hash authentication token.
    hashedToken = hashlib.sha256()
    hashedToken.update(bytes.fromhex(authToken))
    hashedToken = hashedToken.hexdigest()

    #Delete token from authTokens table.
    statement = "DELETE FROM authTokens WHERE hashedToken = %s"
    t=hashedToken
    cursor.execute(statement, (t,))

    #Commit & close.
    mydb.commit()
    cursor.close()

    #Redirect to home page.
    return redirect("/", code = 302)

@app.route("/elephant-maker")
def elephantMaker():

    #Create cursor.
    cursor = mydb.cursor(prepared=True)

    #Grab authentication token from cookies.
    authToken = request.cookies["authToken"]

    # Hash the authToken cookie.
    hashedToken = hashlib.sha256()
    hashedToken.update(bytes.fromhex(authToken))
    hashedToken = hashedToken.hexdigest()

    # Find username associated with authToken
    statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
    t = hashedToken
    cursor.execute(statement, (t,))
    result = cursor.fetchall()

    #If there is a match to a username.
    if (len(result) == 1):

        #Grab username.
        record = result[0][0]

        #Create body: elephant-maker.html with username injected to be served in response.
        body = createMakerPage(record)

        #Make and return the home page response.
        response = make_response()
        response.data = body.encode('utf-8')
        response.content_type = "text/html; charset=utf-8"
        response.content_length = len(body.encode('utf-8'))

        mydb.commit()
        cursor.close()

        return response

    mydb.commit()
    cursor.close()
    return render_template("login.html")

#Elephants are saved in the form:
#[('title', '<title>'), ('file', '<submitted elephants url>')]

@app.route("/save-elephant", methods=["POST"])
def save_elephant():
    print("Form: ",request.form)
    #Save form data to SQL database

    #Redirect back to the elephant maker page
    return render_template("elephant-maker.html")

#Elephants are submitted in the form:
#[('title', '<title>'), ('event', <'event name'>), ('file', '<submitted elephants url>')]

@app.route("/submit-elephant", methods=["POST"])
def submit_elephant():

    #Create cursor.
    cursor = mydb.cursor(prepared=True)

    #Parse data from form: username, title, description, file name, and event.
    username = request.form.get('username')
    title = request.form.get('title')
    description = request.form.get('description')
    file = request.form.get('file')
    event = request.form.get('event')

    #Set initial likes to 0.
    likes = 0

    #Create a new id for the post.
    id = uuid.uuid4().bytes
    hashedID = hashlib.sha256()
    hashedID.update(id)
    hashedID = hashedID.hexdigest()
    #likedby = [] #set list of people who have liked the post

    #Insert post into posts table.
    statement = "INSERT INTO posts(username, title, description, filePath, event, id, likes) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (username, title, description, file, event, str(hashedID), likes)
    cursor.execute(statement, values)

    #Commit changes to database.
    mydb.commit()

    #Create elephant-maker.html for user to serve in response.
    #html = createMakerPage(username)

    # Make and return the elephant-maker response.
    #response = make_response()
    #response.data = html.encode('utf-8')
    #response.content_type = "text/html; charset=utf-8"
    #response.content_length = len(html.encode('utf-8'))

    mydb.commit()
    cursor.close()
    return redirect("/elephant-feed", code = 302)


# HTML for elephant post (need to structure each post individually in a loop)

@app.route("/elephant-feed")
def elephantFeed():

    #Was not able to inject html string into html: elephant_post unused.
    #elephant_post = """
    #<div id="elephant-post.{{post_num}}">
    #						<div class="split" id="section-header">
    #							<h1 class="elephant-post-child">{{elephant_title}}</h1>
    #							<div class="elephant-post-child" id="profile-picture">{{username}}<img src="/static/images/test-profile-picture.png"></div>
    #						</div>
    #						<div class="post-container">
    #						<!-- Image should be what's stored in the database-->
    #							<img class="submitted-elephant" src="/static/images/elephant.png" style="width: 300px; height: 300px;">
    #							<div id="like-button">
    #								<button type="button"  onclick="likeElephant('elephant-post.{{post_num}}')" class="button-like"><i class="fa-regular fa-heart" id="like-child" style="display: block"></i></button>
    #								<!-- When liked, should increment like counter shown on page. Can do this in JS easily, but idk how it will work w the database..
    #								It might be easier to pretend that this like counter incremented up for the user.
    #								It will still happen in the background, but having the page refresh to show this change is probably bad UI since user will be taken to top of page-->
    #								<button type="button"  onclick="unlikeElephant('elephant-post.{{post_num}}')" class="button-unlike"  style="display: none"><i class="fa-solid fa-heart" id="like-child"></i></button>
    #								<p class="like-child" id="like-counter">{like-count} Likes</p>
    #							</div>
    #							<button type="button" id="view-description" onclick="openDesc('elephant-post.{{post_num}}')">View Description</button>
    #						</div>
    #						<div id="description" style="display: none;">
    #							{{description}}
    #						</div>
    #					</div>
    #"""

    #Counter for posts to be injected into elephant-feed.html.
    post_num = 1

    #Basic logic: run a loop and create separate divs for each post in the database
    #IMPORTANT: check elephant-feed.html for better understanding/content

    #Fetch all posts from posts table.
    cursor = mydb.cursor(prepared=True)
    cursor.execute("SELECT * FROM posts")
    post_data = cursor.fetchall()

    #Basic logic: run a loop and create separate divs for each post in the database
    #IMPORTANT: check elephant-feed.html for better understanding/content

    #posts: String to inject into elephant-feed.html.
    posts = ""

    for post in post_data:

        #Use post.html template to create div element of post.
        with open("templates/post.html", 'r') as template:
            f = template.read()
            curr_post = f

            #Inject properties of post based on what's stored in the database.
            curr_post = curr_post.replace("{{elephant_title}}", post[1])
            curr_post = curr_post.replace("{{post_num}}", str(post_num))
            curr_post = curr_post.replace("{{username}}", post[0])
            curr_post = curr_post.replace("{{description}}", post[2])
            curr_post = curr_post.replace("{like-count}", str(post[6]))

            #IMPORTANT: Logic not implemented yet for profile picture and elephant image (displays default)

            post_num += 1

            #Concatenate post to feed string.
            posts = curr_post + posts

    # Following code can be safely deleted (testing to ensure that html replaces successfully)
    #test_post = elephant_post
    #test_post = test_post.replace("{{elephant_title}}", "Test Post")
    #test_post = test_post.replace("{{post_num}}", "3")
    #test_post = test_post.replace("{{username}}", "User1")
    #test_post2 = elephant_post
    #test_post2 = test_post2.replace("{{elephant_title}}", "Next Post")
    #test_post2 = test_post2.replace("{{post_num}}", "4")
    #test_post2 = test_post2.replace("{{username}}", "User2")
    #elephant_title = "Replaced"
    # Delete the section above


    #Grab username.
    username = getUser(request, mydb)
    #print(username)

    #Create f: To store response body which contains injected html of feed.
    f = ''

    if(username != "null"):
        #Create feed-page with username injected.
        f = createFeedPage(username)

    elif(username == "null"):
        with open("templates/elephant-feedNotLoggedIn.html", 'r') as template:
            f = template.read()

    #Inject post feed.
    editFile = f.split('{{posts}}')
    html = editFile[0] + posts + editFile[1]

    response = make_response()
    response.data = html.encode('utf-8')
    response.content_type = "text/html; charset=utf-8"
    response.content_length = len(html.encode('utf-8'))

    mydb.commit()
    cursor.close()
    return response

    #return render_template("elephant-feed.html", posts=posts)
    #return render_template("elephant-feed.html", elephant_title=elephant_title, test_post=Markup(test_post), test_post2=Markup(test_post2))
    #Delete above print statement and replace with commented out line


@app.route("/like", methods = {"POST"})
def like():
    print(json.loads(request.data)) #this returns username and post's div id



@app.route("/unlike", methods = {"POST"})
def unlike():
    print(json.loads(request.data)) #we're not gonna worry about unliking rn


if __name__=='__main__':
    app.run(host="0.0.0.0",port=8080)