from flask import Flask, render_template, request

app=Flask(__name__)
@app.route('/')
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/login")
def login():
    return render_template("login.html")

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

if __name__=='__main__':
    app.run(host="localhost",port=8080)