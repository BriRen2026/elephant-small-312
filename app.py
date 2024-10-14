from flask import Flask, render_template

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


if __name__=='__main__':
    app.run(host="localhost",port=8080)