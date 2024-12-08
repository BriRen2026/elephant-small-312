import json
import base64
import os
from socket import socket


from flask import Flask, render_template, request, make_response, redirect, flash, jsonify, abort, url_for, send_from_directory
from gatekeeper import GateKeeper, IP
import mysql.connector
import hashlib
import datetime


from utilities import *
import uuid
import html
from flask_socketio import SocketIO, emit
import magic


app=Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['DEBUG'] = True
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024 #5MB Limit on posted content
app.secret_key = "elephantsmalls"
app.config["RATELIMIT_ENABLED"] = True
socketio = SocketIO(app, async_mode='eventlet')



@app.after_request #Sets the nosniff header on each responses
def add_security(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    #print(response.headers)
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
        statement = "CREATE TABLE IF NOT EXISTS posts(username VARCHAR(255), title VARCHAR(255),description VARCHAR(255), filePath VARCHAR(255), stamp VARCHAR(255), id VARCHAR(255), likes INT)"
        dbCursor.execute(statement)

        # Create table: likes -> Stores all users who have liked a certain post
        statement = "CREATE TABLE IF NOT EXISTS likes(username VARCHAR(255), postid VARCHAR(255))"
        dbCursor.execute(statement)

        # Create table: comments -> Stores all users and their comments on a specific post
        statement = "CREATE TABLE IF NOT EXISTS comments(username VARCHAR(255), postid VARCHAR(255), comment VARCHAR(255))"
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


#Bans IPs when Rate Limit is reached
gk = GateKeeper(app,
                ip_header="X-Real-IP",
                ban_rule={"count": 1, "window": 2, "duration": 30},   #Ban for 30 seconds after receving 1 report in a 2 second window
                rate_limit_rules=[{"count": 50, "window": 10}],       #Global Rate-limit requests. 20reqs/10seconds
                excluded_methods=["HEAD"])

#Routes for all the front end stuff
@app.route('/static/css/<filename>')
def css(filename):
    print("Serving css: ",filename)
    return send_from_directory('static',"css/"+filename)

@app.route('/static/images/<filename>')
def images(filename):
    #print("Serving image: ",filename)
    return send_from_directory('static',"images/"+filename)


@app.route('/static/javascript/<filename>')
def js(filename):
    #print("Serving JS: ",filename)
    return send_from_directory('static',"javascript/"+filename)


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
            #Add the most recent elephant to the home page
            body = addRecent(body)

            # Make and return the home page response.
            cursor.close()
            return makeHomeResponse(body)

        #If there is more than one authentication token for the user: invalid login.
        else:
            cursor.close()
            f = ""
            with open("templates/home.html", "r") as file:
                f = file.read()
            f = addRecent(f)
            return makeHomeResponse(f)

    #If there is no authToken -> No user is logged in.
    cursor.close()
    f = ""
    with open("templates/home.html", "r") as file:
        f = file.read()
    f = addRecent(f)
    return makeHomeResponse(f)

#Helper function to makes HTML responses with a given body (stored in parameter "info")
def makeHomeResponse(info):
    response = make_response()
    response.data = info.encode('utf-8')
    response.content_type = "text/html; charset=utf-8"
    response.content_length = len(info.encode('utf-8'))
    return response

#Returns the most recent post posted on the elephant site
def addRecent(body):
    #SQL query the posts table. Should exist by default
    cursor = mydb.cursor(prepared=True)
    #Posts are submitted with a timestamp of their submission. Therefore, we can find the latest post by finding the largest date
    statement = "SELECT username, filePath, likes FROM posts WHERE stamp = (SELECT MAX(stamp) FROM posts)"
    cursor.execute(statement)
    result = cursor.fetchall()
    cursor.close()

    print("Result of finding latest post: ",result)
    #If there's no recent post,
    if str(result) == "[]":
        body=body.replace("{{recent}}","/static/images/none.png")
        body=body.replace("{topusername}","--")
        body=body.replace("{likes} Likes","--")

    else:
        path = result[0][1]
        topusername = result[0][0]
        likeCount = str(result[0][2])
        body=body.replace("{{recent}}",path)
        body=body.replace("{topusername}",topusername)
        if likeCount == "1":
            body=body.replace("{likes} Likes",likeCount+" Like")
        else:
            body=body.replace("{likes}",likeCount)

    return body


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
    username = html.escape(request.form.get('username'))[:30]
    password = html.escape(request.form.get('password'))[:30]
    repassword = html.escape(request.form.get('repassword'))[:30]

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
    username = html.escape(request.form.get('username'))[:30]
    password = html.escape(request.form.get('password'))[:30]

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
# @app.route("/leave-comment")
# def leave_comment():
    # username = getUser(request,mydb)
    # comment = html.escape(request.form.get("comment-message"))
    # postid = request.form.get("post_id")
    # print(username," tried leaving a comment on postID ",postid," which says: ",comment)
    #
    # cursor = mydb.cursor(prepared=True)
    #
    # #Add comment to comment database
    # statement2 = "INSERT INTO comments(username, postid, comment) VALUES (%s, %s, %s)"
    # values = (username, postid, comment)
    # cursor.execute(statement2,values)
    #
    # printstatement = "SELECT * FROM comments WHERE postid = %s" #This is printing to sanity check the comments left on each post
    # cursor.execute(printstatement, (postid,))
    # print("Added comment to table: ",cursor.fetchall())
    #
    # mydb.commit()
    # cursor.close()

    # response = make_response()
    # response.data = html.encode('utf-8')
    # response.content_type = "text/html; charset=utf-8"
    # response.content_length = len(html.encode('utf-8'))

    # return make_response('', 204)
    # return redirect("/elephant-feed", code = 302)

@socketio.on("commentData")
def receive_comment_data(comment_data):
    # if request.is_secure:
    #     print("WebSocket connections are secure!!!")
    parsed_data = json.loads(comment_data)
    print("Comment Data: " + str(parsed_data))

    username = parsed_data["username"][:30]
    comment = html.escape(parsed_data["comment"])[:250]
    post_id = parsed_data["post_id"]
    print(username," tried leaving a comment on postID ",post_id," which says: ",comment)

    cursor = mydb.cursor(prepared=True)

    #Add comment to comment database
    statement2 = "INSERT INTO comments(username, postid, comment) VALUES (%s, %s, %s)"
    values = (username, post_id, comment)
    cursor.execute(statement2,values)

    mydb.commit()

    # Temporary Solution/Fix: code below updates the entire feed live instead of just the one comment

    # Permanent Solution/Fix: find a way to ONLY add the one comment and not update the whole feed

    # Implemented: ONLY writes the HTML for the post that was commented on (new comment)
    with open("templates/postComment.html", 'r') as template:
        f = template.read()
        new_comment = f

        new_comment = new_comment.replace("{commenter}", username)
        new_comment = new_comment.replace("{comment-message}", comment)

    emit("feed", json.dumps({"comment": new_comment, "postID": post_id}), broadcast=True)
    cursor.close()

@app.route("/submit-elephant", methods=["POST"])
def submit_elephant():
    print("LOOK HERE",request.form)

    #Create cursor.
    cursor = mydb.cursor(prepared=True)

    # print("Name: ",request.form.get("file"))
    # print("Name: ",html.escape(request.form.get("file")))

    #Parse data from form: username, title, description, file name (NO LONGER DOING EVENTS).
    username = html.escape(request.form.get('username'))[:30]
    print("Username: " + username)
    title = html.escape(request.form.get('title'))[:35]
    print("Title: "+title)
    description = html.escape(request.form.get('description'))[:250]
    print("Description: "+description)
    file = request.files['file']
    print("FILE: ",file)



    stamp = str(datetime.datetime.now())

    #converts html canvas datauri to bytearray for image
    # encData=file.split(',',1)
    # print(encData)
    # decData=base64.b64decode(encData[1])
    # decData=b'\x00\x00'
    # #print(decData)
    blobData=file.read()
    # print("blobdata",blobData)
    # blobBytes=bytearray(blobData)
    # print("blobBytes",blobBytes)
    # encData=base64.b64encode(bytes(blobBytes))
    # print("enc",encData)
    # decData=base64.b64decode(encData)
    # print("dec",decData)

    #Set initial likes to 0.
    likes = 0

    #Create a new id for the post.
    id = uuid.uuid4().bytes
    hashedID = hashlib.sha256()
    hashedID.update(id)
    hashedID = hashedID.hexdigest()
    hashedID = hashedID
    #likedby = [] #set list of people who have liked the post

    #convert initial generated id to string for unique file path
    uuidObj=uuid.UUID(bytes=id)
    uuidFileId=str(uuidObj)
    path="static/canvasPost/"+"canv"+uuidFileId
    with open(path,"wb") as f:
        f.write(blobData)
        # f.write(b'\x00\x00\x00')
    f.close()

    #Insert post into posts table.
    statement = "INSERT INTO posts(username, title, description, filePath, stamp, id, likes) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    values = (username, title, description, path, stamp, str(hashedID), likes)
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

    print("RIGHT BEFORE REDIRECT")
    return redirect('/elephant-feed',code=302)

# HTML for elephant post (need to structure each post individually in a loop)
# IMPORTANT: variable below is NOT being used anymore (pot for hashedIDs)
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

    #Grab username of user viewing the page
    username = getUser(request, mydb)
    #print(username)

    #Basic logic: run a loop and create separate divs for each post in the database
    #IMPORTANT: check elephant-feed.html for better understanding/content

    # Fetch all comments from comments table
    cursor = mydb.cursor(prepared=True)
    cursor.execute("SELECT * FROM comments")
    comment_data = cursor.fetchall()

    comments = {}

    for comment in comment_data:

        post_id = comment[1]

        with open("templates/postComment.html", 'r') as template:
            f = template.read()
            curr_comment = f

            curr_comment = curr_comment.replace("{commenter}", comment[0])
            curr_comment = curr_comment.replace("{comment-message}", comment[2])

            if not post_id in comments:
                comments[post_id] = curr_comment
            else:
                comment_section = comments[post_id]
                comments[post_id] = comment_section + curr_comment


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
            # Line below was originally str(post_num): change so post ids are consistent for every user
            curr_post = curr_post.replace("{{post_num}}", str(post[5]))
            # IMPORTANT: check above comment
            curr_post = curr_post.replace("{{username}}", curr_username)
            curr_post = curr_post.replace("{{description}}", post[2])
            curr_post = curr_post.replace("{like-count}", str(post[6]))
            curr_post = curr_post.replace("{{post_id}}", str(post[5])) #sets post ID in hidden form
            curr_post = curr_post.replace("{{elephant_image}}", str(post[3]))
            curr_post = curr_post.replace("{{pfp}}", pfp)

            if post[5] in comments:
                curr_post = curr_post.replace("{{comments}}", comments[post[5]])
            else:
                curr_post = curr_post.replace("{{comments}}", "No Comments")

            #(Written by Jenna)
            #For liking and unliking, we must check the postIDLIkedBy database for the current user on the page
            #If it comes back as [], then the user viewing the page has NOT liked this post
            displayLike = "SELECT * FROM likes WHERE username = %s AND postid = %s"
            cursor.execute(displayLike, (username, str(post[5])))
            result = str(cursor.fetchall())
            print("Has user liked before?: ",result)

            #< button type = "button" onclick = "likeElephant('elephant-post.{{post_num}}')" class ="button-like" style="display: block; background: none; border: 0;" > < i class ="fa-regular fa-heart"  id="like-child" > < / i > < / button >
            #< button type = "button" onclick = "unlikeElephant('elephant-post.{{post_num}}')" class ="button-unlike" style="display: block; background: none; border: 0;" > < i class ="fa-solid fa-heart"  id="like-child" > < / i > < / button >

            # IMPORTANT: changed postIDs to hashedIDs instead of global post_num for
            # consistent identification for every user

            #User has not liked the post
            unlikeHTMLBlock = "<button type = 'button' style='display: block; background: none; border:0;' class='button-unlike' onclick = "+ 'unlikeElephant("elephant-post.'+str(post[5])+'")>'+" <i class ='fa-solid fa-heart' id='like-child'></i></button>"
            likeHTMLBlock = "<button type = 'button' style='display: block; background: none; border:0;' class='button-like' onclick = "+ 'likeElephant("elephant-post.'+str(post[5])+'")>'+" <i class ='fa-regular fa-heart' id='like-child'></i></button>"

            #User has liked the post
            unlikeHTMLNone = "<button type = 'button' style='display: none; background: none; border:0;' class='button-unlike' onclick = " + 'unlikeElephant("elephant-post.' + str(post[5]) + '")>' + " <i class ='fa-solid fa-heart' id='like-child'></i></button>"
            likeHTMLNone = "<button type = 'button'  style='display: none; background: none; border:0;' class='button-like' onclick = " + 'likeElephant("elephant-post.' + str(post[5]) + '")>' + " <i class ='fa-regular fa-heart' id='like-child'></i></button>"

            # IF user has not liked the post, display: block the likeHTML and display:none the unlikeHTML
            if result == "[]":
                print("User has not liked the post")
                curr_post = curr_post.replace("{{like-status}}",likeHTMLBlock+unlikeHTMLNone)

            #IF user has liked the post, display: none the likeHTML and display:block the unlikeHTML
            else:
                print("User has liked the post")
                curr_post = curr_post.replace("{{like-status}}",unlikeHTMLBlock+likeHTMLNone)



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

    #Do not allow non-logged in users to view posted elephants
    elif(username == "null"):
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

# When user navigates to elephant feed, this event triggers in js of elephant-feed.html
@socketio.on("connect")
def live_comment_feed():
    # Add logic here to receive and display submitted elephant posts live (while loop?)
    # Comment: while loop was not needed (check receive_post_data function below)
    # if request.is_secure:
    #     print("WebSocket connections are secure!!!")
    print("Hit connection path!")

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

# Websocket disconnects automatically upon refresh or leaving elephantFeed page
@socketio.on("disconnect")
def handle_disconnect():
    # Disconnect websocket when user leaves elephantFeed page
    for user in list(activeUsers):
        if (activeUsers[user] == request.sid):
            userStates.pop(user, None)
            activeUsers.pop(user, None)
            inGame.pop(user, None)

    sendList = json.dumps(userStates)
    # Client: Updates lobby.
    emit("sendUser", {"users": sendList}, broadcast=True)

    print("Disconnected!")

@app.route("/unlike", methods = {"POST"})
def unlike():
    data = json.loads(request.data)
    username = data["username"][:30]
    postid = data["id"]
    print("User ",username," is liking postID: ",postid)

    cursor = mydb.cursor(prepared=True)

    # Now, we shooould be sure that a table exists with this posts usernames of people who've currently liked it
    # Check if the user even HAS liked this post
    #Just checking if an instance of the user liking this exists at all, so check for 1 column (Shouldn't SELECT *)
    statement2 = "SELECT username FROM likes WHERE username = %s AND postid = %s"
    cursor.execute(statement2, (username, postid))
    result = str(cursor.fetchall())
    print("Did the user like this post?: ", result)

    #if the user has liked this post, we can allow them to unlike
    if result != "[]":
        print("User has liked this post already, allow them to unlike")
        statement3 = "DELETE FROM likes WHERE username = %s AND postid = %s"
        cursor.execute(statement3,(username,postid))
        #Update like count on post
        statement4 = "UPDATE posts SET likes = likes-1 WHERE id = %s"
        cursor.execute(statement4, (postid,))
    else:
        print("YOU CANNOT UNLIKE THIS!!!")
        abort(400)

    mydb.commit()
    cursor.close()

    return redirect("/elephant-feed", code = 302)

@app.route("/like", methods = {"POST"})
def like():
    data = json.loads(request.data)
    username = data["username"][:30]
    postid = data["id"]
    print("User ",username," is liking postID: ",postid)

    cursor = mydb.cursor(prepared=True)

    #Likes database should already be made.
    #Now that the table exists, we HAVE to make sure the current user hasn't liked this post already
    #Just checking if an instance of the user liking this exists at all, so check for 1 column (Shouldn't SELECT *)
    statement2 = "SELECT username FROM likes WHERE username = %s AND postid = %s"
    cursor.execute(statement2, (username,postid))
    result = str(cursor.fetchall())
    print("Did the user like this post?: ",result)

    if result == "[]":
        print("User did not like this post already")
        statement = "INSERT INTO likes(username, postid) VALUES (%s, %s)"
        values = (username, postid)
        cursor.execute(statement,values)
        #Update like count on post
        statement4 = "UPDATE posts SET likes = likes+1 WHERE id = %s"
        cursor.execute(statement4, (postid,))

    else:
        print("YOU CANNOT LIKE AGAIN!!!!!!!!!!!!!!!!!!!!!!!")
        abort(400)


    mydb.commit()
    cursor.close()

    return redirect("/elephant-feed", code = 302)


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

            body = createProfilePage(username, pfp)
        else:
            return render_template("register.html")
    else:
        return render_template("register.html")

    response = make_response()
    response.data = body.encode('utf-8')
    response.content_type = "text/html; charset=utf-8"
    response.content_length = len(body.encode('utf-8'))

    mydb.commit()
    cursor.close()

    print("Body :" + response.data.decode('utf-8'))
    return response

#Gets mime type via file signature (Doesn't trust user input)
def get_mimetype(data: bytes) -> str:
    f = magic.Magic(mime=True)
    return f.from_buffer(data)

# Submit button for changing user profile picture
@app.route("/change-pfp", methods = {"POST"})
def change_pfp():
    cursor = mydb.cursor(prepared=True)

    if "authToken" in request.cookies:
        # Retrieve user file and save to disk

        data = request.files['pfp']
        file_bytes = data.read(2048) #First few bytes of the file will contain the mime type
        # Determine the MIME type
        mime = magic.from_buffer(file_bytes, mime=True)
        # Reset file pointer to the beginning
        data.seek(0)
        print("Mime type of uploaded file: ",str(mime))

        #only accept IMAGES and GIFS
        if mime == "image/gif" or mime == "image/jpeg" or mime == "image/png":
            filename = str(uuid.uuid4())
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

                #DELETE the old profile pic if a previous one was updated
                #We need to make sure we don't have too much storage taken up
                statement = "SELECT profilePicture FROM logins WHERE username = %s"
                cursor.execute(statement, (username,))
                previousResult = cursor.fetchall()

                if len(previousResult) == 1:
                    if os.path.exists(previousResult[0][0][1:]): #Make sure we only delete it if it exists (dc forcerecreate may remove)
                        if previousResult[0][0] != "/static/images/test-profile-picture.png": #Don't delete the test-profile-picture
                            print("Before removing: ",os.listdir("static/pfp"))
                            os.remove(previousResult[0][0][1:])
                            print("Previous pfp deleted from storage")
                            print("After removing: ",os.listdir("static/pfp"))

                #Update the value stored in logins to be the new directory for a user's profile picture
                statement = "UPDATE logins SET profilePicture=%s WHERE username = %s"
                cursor.execute(statement, ("/static/pfp/" + filename, username))

        else:
            print("Unallowed File Type")
            return "<h1>403</h1>Allowed File Types: .jpg, .png, .gif",403

    # Redirect to home page
    mydb.commit()
    cursor.close()
    return redirect("/profile", code=302)

@app.route("/testgame")
def testGame():
    return render_template("testgame2.html")

@app.route("/deleteDB")
def deleteDB():
    cursor = mydb.cursor(prepared=True)
    statement = "DROP DATABASE credentials"
    cursor.execute(statement)

#Websocket Users -> READY Status
userStates = {}
activeUsers = {}
#InSession -> Indicates if there is a game in progress.
inSession = False

#joinClient: Handles when a user enters the lobby.
@socketio.on('create')
def joinClient(username):
    print(username + " has joined!")
    user = json.loads(username)
    activeUsers[user] = request.sid
    userStates[user] = "NOT READY"
    sendList = json.dumps(userStates)

    #Client: Updates lobby.
    emit("sendUser", {"users": sendList}, broadcast=True)

#readyOrNot: Handles user clicking READY.
@socketio.on('userReady')
def readyOrNot(username, state):
    print(username + " is ready!")
    user = request.sid

    global inSession
    #If game is not taking place, accept ready.
    if (inSession == False) :
        userStates[username] = state
        sendList = json.dumps(userStates)

        #Client: Updates lobby.
        emit("sendUser", {"users": sendList}, broadcast=True)

    #If game is taking place, make user wait.
    if (inSession == True) :

        #Client: Sends wait message.
        emit("wait", to = user)

import time
#inGame: username -> sessionID, for users in game.
inGame = {}

#readySetGo: Handles countdown timer in lobby.
@socketio.on('startTimer')
def readySetGo():
    print("Game is starting!")

    #Countdown from 15 to start game.
    for sec in range(10,-1,-1):
        constructTime = str(sec)
        print("Time left till start: " + constructTime)

        #Client: Client can see how much time is left till game starts.
        emit("countdown", json.dumps(constructTime), broadcast=True)
        socketio.sleep(1)

    global userStates

    #inGame: Stores users that are in game.
    global inGame
    for user in userStates.keys():
        inGame[user] = userStates[user]

    #userStates: Clears so new users can wait in lobby after game starts.
    userStates.clear()

    #Client: Those in lobby will be pushed to the dressing room.
    emit("sendFashionMaker", broadcast= True)


#fight: Handles countdown timer in Dressing Room.
@socketio.on('startCompetition')
def fight():

    #Indicate that there is a game in session on server.
    global inSession
    inSession = True

    #Countdown from 60 till end game.
    for sec in range(60,-1,-1):
        constructTime = str(sec)
        print("Time left till game ends: " + constructTime)
        emit("countdownCompetition", json.dumps(constructTime), broadcast=True)
        socketio.sleep(1)

    #Client: Opens submit screen for forced submission.
    emit("submitForCompetition", broadcas=True)

#count: Keeps track of how many users have submitted their elephants.
countUsers = 0

#collect: Handles/counts client submission to determine when to update inSession.
@socketio.on('collectUsers')
def collect():
    global countUsers
    countUsers = countUsers + 1
    print(countUsers)

    global inGame
    print(len(inGame))

    #If all submissions are received.
    if(countUsers == len(inGame)):
        global inSession
        inSession = False
        inGame.clear()


#Route for party route, elephant-maker-compete.
@app.route("/elephant-maker-compete")
def elephantMakerCompete():

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
            body = createMakerCompetePage(record, pfp)

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

if __name__=='__main__':
    socketio.run(app, host='0.0.0.0', port=8080, use_reloader=False, log_output=False)
    # app.run(host="0.0.0.0",port=8080)