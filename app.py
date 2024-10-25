from flask import Flask, render_template, request, make_response, redirect, flash
import mysql.connector
import hashlib
from utilities import *
import uuid
from markupsafe import Markup

app=Flask(__name__)
# app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "elephantsmalls"

# Create credentials database if it doesn't exist at startup.

@app.after_request #sets the nosniff header on each response
def add_security(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response
def createDatabase():
    try:
        myServer = mysql.connector.connect(host = 'mysql', user='root', password='iloveelephantsmalls')
        cursor = myServer.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {'credentials'}")
        myServer.commit()
        cursor.close()
        myServer.close()
    except Exception:
        print("Database create failed.")

# Create the database on app startup
createDatabase()

mydb = mysql.connector.connect(host = "mysql", user = "root", password = "iloveelephantsmalls", database = "credentials")

@app.route('/', methods = ["POST", "GET"])
def home():
    cursor = mydb.cursor(prepared=True)

    #If an authToken is set in cookies -> A user is logged in.
    if "authToken" in request.cookies:
        authToken = request.cookies["authToken"]

        #Hash the authToken cookie.
        hashedToken = hashlib.sha256()
        hashedToken.update(bytes.fromhex(authToken))
        hashedToken = hashedToken.hexdigest()

        #Find username associated with authToken
        statement = "SELECT username FROM authTokens WHERE hashedToken = %s"
        t=hashedToken
        cursor.execute(statement,(t,))
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

    cursor.close()
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
    cursor = mydb.cursor(prepared=True)

    #Create logins table.
    statement = "CREATE TABLE IF NOT EXISTS logins(username VARCHAR(255), hashedPass VARCHAR(255))"
    cursor.execute(statement)

    #Create authTokens table if it doesn't exist.
    cursor = mydb.cursor(prepared=True)
    statement = "CREATE TABLE IF NOT EXISTS authTokens(username VARCHAR(255), hashedToken VARCHAR(255))"
    cursor.execute(statement)

    #Parse username, password, and reentered password.
    username = request.form.get('username')
    password = request.form.get('password')
    repassword = request.form.get('repassword')

    #Find login for input username.
    statement = "SELECT * FROM logins WHERE username = %s"
    u=username
    cursor.execute(statement,(u,))
    result = cursor.fetchall()

    #Computes how many instances are associated with that username: should be either 0 or 1.
    exists = 0
    for element in result:
        exists += 1

    #If there is not a registered user with the username:
    if exists == 0:

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
            generateAuthToken(username, cursor, response)

            # Save changes to database.
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

    if (len(result) == 0):
        flash("Invalid username/password.")
        return render_template("login.html")


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

        cursor.close()
        return response

    #If the passwords do not match, don't authenticate.
    else:
        flash("Invalid username/password.")
        cursor.close()
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
    statement = "DELETE FROM authTokens WHERE hashedToken = %s"
    t=hashedToken
    cursor.execute(statement, (t,))
    mydb.commit()
    cursor.close()
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

# HTML for elephant post (need to structure each post individually in a loop)
elephant_post = """
<div id="elephant-post.{{post_num}}">
						<div class="split" id="section-header">
							<h1 class="elephant-post-child">{{elephant_title}}</h1>
							<div class="elephant-post-child" id="profile-picture">{{username}}<img src="/static/images/test-profile-picture.png"></div>
						</div>
						<div class="post-container">
						<!-- Image should be what's stored in the database-->
							<img class="submitted-elephant" src="/static/images/elephant.png" style="width: 300px; height: 300px;">
							<div id="like-button">
								<button type="button"  onclick="likeElephant('elephant-post.{{post_num}}')" class="button-like"><i class="fa-regular fa-heart" id="like-child" style="display: block"></i></button>
								<!-- When liked, should increment like counter shown on page. Can do this in JS easily, but idk how it will work w the database..
								It might be easier to pretend that this like counter incremented up for the user.
								It will still happen in the background, but having the page refresh to show this change is probably bad UI since user will be taken to top of page-->
								<button type="button"  onclick="unlikeElephant('elephant-post.{{post_num}}')" class="button-unlike"  style="display: none"><i class="fa-solid fa-heart" id="like-child"></i></button>
								<p class="like-child" id="like-counter">{like-count} Likes</p>
							</div>
							<button type="button" id="view-description" onclick="openDesc('elephant-post.{{post_num}}')">View Description</button>
						</div>
						<div id="description" style="display: none;">
							{{description}}
						</div>
					</div>
"""
post_num = 1
@app.route("/elephant-feed")
def elephantFeed():
    # Basic logic: run a loop and create separate divs for each post in the database
    # IMPORTANT: check elephant-feed.html for better understanding/content

    # post_data = ... (retrieve all posts from database)
    posts = ""

    # for post in post_data:
    #     curr_post = elephant_post
    #     curr_post = curr_post.replace("{{elephant_title}}", Post Title)
    #     curr_post = curr_post.replace("{{post_num}}", str(post_num))
    #     curr_post = curr_post.replace("{{username}}", Post Username)
    #     curr_post = curr_post.replace("{{description}}", Post Description)
    #     IMPORTANT: Logic not implemented yet for profile picture and elephant image (displays default)
    #     post_num += 1
    #     posts += curr_post

    # Following code can be safely deleted (testing to ensure that html replaces successfully)
    test_post = elephant_post
    test_post = test_post.replace("{{elephant_title}}", "Test Post")
    test_post = test_post.replace("{{post_num}}", "3")
    test_post = test_post.replace("{{username}}", "User1")
    test_post2 = elephant_post
    test_post2 = test_post2.replace("{{elephant_title}}", "Next Post")
    test_post2 = test_post2.replace("{{post_num}}", "4")
    test_post2 = test_post2.replace("{{username}}", "User2")
    elephant_title = "Replaced"
    # Delete the section above

    # Actual return statement: return render_template("elephant-feed.html", posts=posts)
    return render_template("elephant-feed.html",
                           elephant_title=elephant_title, test_post=Markup(test_post), test_post2=Markup(test_post2))
    # Delete above print statement and replace with commented out line

if __name__=='__main__':
    app.run(host="0.0.0.0",port=8080)