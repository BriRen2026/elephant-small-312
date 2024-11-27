import json
import base64
from socket import socket

from flask import Flask, render_template, request, make_response, redirect, flash, jsonify
import mysql.connector
import hashlib

from werkzeug.utils import secure_filename

from utilities import *
import uuid
from markupsafe import Markup
import html
from flask_socketio import SocketIO, emit

app=Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['DEBUG'] = True
app.secret_key = "elephantsmalls"
socketio = SocketIO(app, async_mode='eventlet')

@app.after_request #Sets the nosniff header on each responses
def add_security(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    print(response.headers)
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
        statement = "CREATE TABLE IF NOT EXISTS logins(username VARCHAR(255), hashedPass VARCHAR(255), profilePicture VARCHAR(255))"
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
        hashedToken=hashlib.sha256(authToken.encode()).hexdigest()
        # hashedToken = hashlib.sha256()
        # hashedToken.update(bytes.fromhex(authToken))
        # hashedToken = hashedToken.hexdigest()

        #Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
        t = hashedToken
        cursor.execute(statement, (t,))
        result = cursor.fetchall()

        #If there is only one authentication token for the user.
        if(len(result) == 1):

            #Grab username from record in authTokens.
            record = result[0][0]

            statement = "SELECT profilePicture FROM logins WHERE username = %s"
            cursor.execute(statement, (record,))
            result = cursor.fetchall()
            pfp = result[0][0]

            #Create body: homeLoggedIn.html with username injected to be served in response.
            body = createHomePage(record, pfp)

            # Make and return the home page response.
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
    statement = "CREATE TABLE IF NOT EXISTS logins(username VARCHAR(255), hashedPass VARCHAR(255), profilePicture VARCHAR(255))"
    cursor.execute(statement)

    #Create authTokens table if it doesn't exist (for precautions).
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Parse username, password, and reentered password from form.
    username = html.escape(request.form.get('username'))
    password = html.escape(request.form.get('password'))
    repassword = html.escape(request.form.get('repassword'))

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
            statement = "INSERT INTO logins(username, hashedPass, profilePicture) VALUES (%s, %s, %s)"
            values = (username, stringHash, '/static/images/test-profile-picture.png')
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
    username = html.escape(request.form.get('username'))
    password = html.escape(request.form.get('password'))

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

        # statement = "SELECT profilePicture FROM logins WHERE username = %s"
        # cursor.execute(statement, (record,))
        # result = cursor.fetchall()
        # pfp = result[0][0]

        #Create homeLoggedIn.html with injected username for response.
        createHomePage(username, "/static/images/test-profile-picture.png")

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
    cursor = mydb.cursor(prepared=True)

    #Create authTokens table if it doesn't exist.
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Take authToken from cookies.
    authToken = request.cookies["authToken"]

    #Hash authentication token.
    # hashedToken = hashlib.sha256()
    # hashedToken.update(bytes.fromhex(authToken))
    # hashedToken = hashedToken.hexdigest()
    hashedToken = hashlib.sha256(authToken.encode()).hexdigest()

    #Delete token from authTokens table.
    statement = "DELETE FROM authTokens WHERE hashedToken = %s"
    t=hashedToken
    cursor.execute(statement, (t,))

    #Commit & close.
    mydb.commit()
    cursor.close()

    response = make_response(redirect("/", code = 302))
    response.content_type = "text/html; charset=utf-8"
    response.set_cookie("authToken", httponly=True, max_age=-100)

    #Redirect to home page.
    return response

@app.route("/elephant-maker")
def elephantMaker():

    body = ""

    #Create cursor.
    cursor = mydb.cursor(prepared=True)

    if 'authToken' in request.cookies:
        #Grab authentication token from cookies.
        authToken = request.cookies["authToken"]

        # Hash the authToken cookie.
        hashedToken = hashlib.sha256(authToken.encode()).hexdigest()
        # hashedToken = hashlib.sha256()
        # hashedToken.update(bytes.fromhex(authToken))
        # hashedToken = hashedToken.hexdigest()

        # Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
        t = hashedToken
        cursor.execute(statement, (t,))
        result = cursor.fetchall()

        #If there is a match to a username.
        if (len(result) == 1):
            # Grab username.
            record = result[0][0]

            statement = "SELECT profilePicture FROM logins WHERE username = %s"
            cursor.execute(statement, (record,))
            result = cursor.fetchall()
            pfp = result[0][0]

            # Create body: elephant-maker.html with username injected to be served in response.
            body = createMakerPage(record, pfp)

            # Make and return the home page response.
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
    else:
        return render_template("register.html")

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
@app.route("/leave-comment", methods=["POST"])
def leave_comment():

    username = getUser(request,mydb)
    comment = html.escape(request.form.get("comment-message"))
    postid = request.form.get("post_id")

    print(username," tried leaving a comment on postID ",postid," which says: ",comment)

    #We CANNOT store lists in SQL as it's a relational database
    #We must create a table for each post where a comment is left
    cursor = mydb.cursor(prepared=True)

    #First, create a table if it doesn't already exist where the name of the table is the unique postID
    #The columns will contain the commenter's username and their comment
    #This could theoretically also be used to store the likes associated with this post, but im not thinking ab that yet
    statement = "CREATE TABLE IF NOT EXISTS postid(username VARCHAR(255), comment VARCHAR(255))"
    cursor.execute(statement)

    #Now, the table is created whether it existed or not. Either way, we must insert our data into it.
    statement2 = "INSERT INTO postid(username, comment) VALUES (%s, %s)"
    values = (username, comment)
    cursor.execute(statement2,values)

    printstatement = "SELECT * FROM postid"
    cursor.execute(printstatement)
    print("Added comment to table: ",cursor.fetchall())

    mydb.commit()
    cursor.close()

    return redirect("/elephant-feed", code = 302)

@app.route("/submit-elephant", methods=["POST"])
def submit_elephant():

    #Create cursor.
    cursor = mydb.cursor(prepared=True)

    # print("Name: ",request.form.get("file"))
    # print("Name: ",html.escape(request.form.get("file")))

    #Parse data from form: username, title, description, file name, and event.
    username = html.escape(request.form.get('username'))
    print("Username: " + username)
    title = html.escape(request.form.get('title'))
    description = html.escape(request.form.get('description'))
    file = html.escape(request.form.get('file'))
    print("FILE: "+file)
    event = html.escape(request.form.get('event'))

    #converts html canvas datauri to bytearray for image
    encData=file.split(',',1)
    print(encData)
    decData=base64.b64decode(encData[1])
    #print(decData)

    #Set initial likes to 0.
    likes = 0

    #Create a new id for the post.
    id = uuid.uuid4().bytes
    hashedID = hashlib.sha256()
    hashedID.update(id)
    hashedID = hashedID.hexdigest()
    #likedby = [] #set list of people who have liked the post

    #convert initial generated id to string for unique file path
    uuidObj=uuid.UUID(bytes=id)
    uuidFileId=str(uuidObj)
    path="static/canvasPost/"+"canv"+uuidFileId
    with open(path,"wb") as f:
        f.write(decData)
    f.close()

    #Insert post into posts table.
    statement = "INSERT INTO posts(username, title, description, filePath, event, id, likes) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (username, title, description, path, event, str(hashedID), likes)
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
post_num = 1

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
    global post_num

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
        # print("Post: ",post)

        curr_username = post[0]
        statement = "SELECT profilePicture FROM logins WHERE username = %s"
        cursor.execute(statement, (curr_username,))
        result = cursor.fetchall()
        pfp = result[0][0]

        #Use post.html template to create div element of post.
        with open("templates/post.html", 'r') as template:
            f = template.read()
            curr_post = f

            #Inject properties of post based on what's stored in the database.
            #Database infos stored in format = (username, title, description, file, event, str(hashedID), likes)
            curr_post = curr_post.replace("{{elephant_title}}", post[1])
            curr_post = curr_post.replace("{{post_num}}", str(post_num))
            curr_post = curr_post.replace("{{username}}", curr_username)
            curr_post = curr_post.replace("{{description}}", post[2])
            curr_post = curr_post.replace("{like-count}", str(post[6]))
            curr_post = curr_post.replace("{{post_id}}", str(post[5])) #sets post ID in hidden form
            curr_post = curr_post.replace("{{elephant_image}}", str(post[3]))
            curr_post = curr_post.replace("{{pfp}}", pfp)



            #IMPORTANT: Logic not implemented yet for profile picture

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
        # Retrieve pfp associated with user
        statement = "SELECT profilePicture FROM logins WHERE username = %s"
        cursor.execute(statement, (username,))
        result = cursor.fetchall()
        pfp = result[0][0]

        #Create feed-page with username injected.
        f = createFeedPage(username, pfp)

    elif(username == "null"):
        # with open("templates/elephant-feedNotLoggedIn.html", 'r') as template:
        #    f = template.read()
        #User is not logged in. Return to home page.
        return render_template("register.html")

        #return redirect("/login", code = 302)

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

# # When user navigates to elephant feed, this event triggers in js of elephant-feed.html
# @socketio.on("connect")
# def live_elephantFeed():
#     # Add logic here to receive and display submitted elephant posts live (while loop?)
#     # Comment: while loop was not needed (check receive_post_data function below)
#     print("Hit connection path!")
#
# @socketio.on("postData")
# def receive_post_data(post_data):
#     global post_num
#
#     parsed_data = json.loads(post_data)
#     # print("Post Data: " + str(parsed_data))
#
#     cursor = mydb.cursor(prepared=True)
#     cursor.execute("SELECT * FROM posts")
#     post_data = cursor.fetchall()
#
#     # Contains HTML of all posts to send to JS script to display in real-time
#     posts_dict = {}
#
#     # Following code: taken from /submit_elephant route
#     for post in post_data:
#
#         curr_username = post[0]
#         statement = "SELECT profilePicture FROM logins WHERE username = %s"
#         cursor.execute(statement, (curr_username,))
#         result = cursor.fetchall()
#         pfp = result[0][0]
#
#         with open("templates/post.html", 'r') as template:
#             f = template.read()
#             curr_post = f
#
#             curr_post = curr_post.replace("{{elephant_title}}", post[1])
#             curr_post = curr_post.replace("{{post_num}}", str(post_num))
#             curr_post = curr_post.replace("{{username}}", curr_username)
#             curr_post = curr_post.replace("{{description}}", post[2])
#             curr_post = curr_post.replace("{like-count}", str(post[6]))
#             curr_post = curr_post.replace("{{post_id}}", str(post[5]))  # sets post ID in hidden form
#             curr_post = curr_post.replace("{{elephant_image}}", str(post[3]))
#             curr_post = curr_post.replace("{{pfp}}", pfp)
#
#             posts_dict[post_num] = curr_post
#             post_num += 1
#
#     # Create and add HTML for new post
#     id = uuid.uuid4().bytes
#     hashedID = hashlib.sha256()
#     hashedID.update(id)
#     hashedID = hashedID.hexdigest()
#     with open("templates/post.html", 'r') as template:
#         f = template.read()
#         new_post = f
#
#         elephant_image_path = "/static/images/" + str(parsed_data["elephant_image"].split("images/")[1])
#         pfp_path = "/static/images/" + str(parsed_data["pfp"].split("images/")[1])
#
#         new_post = new_post.replace("{{elephant_title}}", parsed_data["elephant_title"])
#         new_post = new_post.replace("{{post_num}}", str(post_num))
#         new_post = new_post.replace("{{username}}", parsed_data["username"])
#         new_post = new_post.replace("{{description}}", parsed_data["description"])
#         new_post = new_post.replace("{like-count}", str(0))
#         new_post = new_post.replace("{{post_id}}", str(hashedID))  # sets post ID in hidden form
#         new_post = new_post.replace("{{elephant_image}}", elephant_image_path)
#         new_post = new_post.replace("{{pfp}}", pfp_path)
#
#         posts_dict[post_num] = new_post
#         post_num += 1
#
#     # print(posts_dict)
#
#     # This updates the feed in real-time (broadcast=True needed to send to all connected users)
#     emit("feed", json.dumps(posts_dict), broadcast=True)
#
# # Websocket disconnects automatically upon refresh or leaving elephantFeed page
# @socketio.on("disconnect")
# def handle_disconnect():
#     # Disconnect websocket when user leaves elephantFeed page
#     print("Disconnected!")

@app.route("/like", methods = {"POST"})
def like():
    print ("data:")
    print(json.loads(request.data)) #this returns username and post's div id
    data = json.loads(request.data)
    username = data["username"]
    theid = data["id"]

    cursor = mydb.cursor(prepared=True)

    statement2 = "SELECT * FROM likes WHERE username = %s AND postID = %s"
    cursor.execute(statement2, (username, theid,))
    result = cursor.fetchall()
    print("result: ")
    print(result)
    if len(result) != 0:
        return redirect("/elephant-feed", code=302)

    statement = "UPDATE posts SET likes = likes+1 WHERE id = %s"
    cursor.execute(statement, (theid,))
    statement3 = "INSERT INTO likes(username, postID) VALUES (%s, %s)"
    cursor.execute(statement3, (username, theid,))
    statement = "SELECT * FROM likes"
    cursor.execute(statement)
    print("likes content:")
    print(cursor.fetchall())
    mydb.commit()
    cursor.close()
    return redirect("/elephant-feed", code=302)

@app.route("/profile")
def profile():
    cursor = mydb.cursor(prepared=True)

    if "authToken" in request.cookies:
        auth_token = request.cookies["authToken"]
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()

        # Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
        t = hashed_token
        cursor.execute(statement, (t,))
        result = cursor.fetchall()

        if len(result) == 1:
            username = result[0][0]

            # Retrieve pfp associated with user account
            statement = "SELECT profilePicture FROM logins WHERE username = %s"
            cursor.execute(statement, (username,))
            result = cursor.fetchall()
            pfp = result[0][0]
            print("Profile Pic: " + pfp)

            body = createProfilePage(username, pfp)
        else:
            body = createProfilePage("Guest", "/static/images/test-profile-picture.png")
    else:
        body = createProfilePage("Guest", "/static/images/test-profile-picture.png")

    response = make_response()
    response.data = body.encode('utf-8')
    response.content_type = "text/html; charset=utf-8"
    response.content_length = len(body.encode('utf-8'))

    mydb.commit()
    cursor.close()

    print("Body :" + response.data.decode('utf-8'))
    return response

# Submit button for changing user profile picture
@app.route("/change-pfp", methods = {"POST"})
def change_pfp():
    cursor = mydb.cursor(prepared=True)

    if "authToken" in request.cookies:
        # Retrieve user file and save to disk
        data = request.files["pfp"]
        filename = secure_filename(data.filename)
        pfp = data.read()
        with open("static/pfp/" + filename, "wb") as f:
            f.write(pfp)

        # Find associated user and update their pfp (with path to their pfp)
        auth_token = request.cookies["authToken"]
        hashed_token = hashlib.sha256(auth_token.encode()).hexdigest()

        # Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
        t = hashed_token
        cursor.execute(statement, (t,))
        result = cursor.fetchall()

        if len(result) == 1:

            username = result[0][0]

            # Update user pfp
            statement = "UPDATE logins SET profilePicture=%s WHERE username = %s"
            cursor.execute(statement, ("/static/pfp/" + data.filename, username))

            # statement = "SELECT profilePicture FROM logins WHERE username = %s"
            # cursor.execute(statement, (username,))
            # result = cursor.fetchall()
            # print("Result: " + str(result))

    # Redirect to home page
    mydb.commit()
    cursor.close()
    return redirect("/profile", code=302)

# We aren't worried about unliking yet
@app.route("/unlike", methods = {"POST"})
def unlike():
    print(json.loads(request.data)) #we're not gonna worry about unliking rn
    data = json.loads(request.data)
    username = data["username"]
    theid = data["id"]

    cursor = mydb.cursor(prepared=True)
    statement2 = "SELECT * FROM likes WHERE username = %s AND postID = %s"
    cursor.execute(statement2, (username, theid,))
    result = cursor.fetchall()
    if len(result) == 0:
        return redirect("/elephant-feed", code=302)
    statement = "UPDATE posts SET likes = likes-1 WHERE id = %s"
    cursor.execute(statement, (theid,))
    statement3 = "DELETE FROM likes(username, postID) VALUES (%s, %s)"
    cursor.execute(statement3, (username, theid,))
    statement = "SELECT * FROM likes"
    cursor.execute(statement)
    print("likes content:")
    print(cursor.fetchall())
    mydb.commit()
    cursor.close()
    return redirect("/elephant-feed", code=302)

@app.route("/testgame")
def testGame():
    return render_template("testgame.html")

@app.route("/deleteDB")
def deleteDB():
    cursor = mydb.cursor(prepared=True)
    statement = "DROP DATABASE credentials"
    cursor.execute(statement)

if __name__=='__main__':
    socketio.run(app, host='0.0.0.0', port=8080, use_reloader=False, log_output=False)
    # app.run(host="0.0.0.0",port=8080)