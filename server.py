from flask import Flask,render_template

app = Flask("__name__")
@app.route("/")
def home():
    return render_template("welcome.html")

@app.route('/login')
def Login():
    return render_template("Login.html")

@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/home')
def homeScreen():
    return render_template("home.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")

@app.route('/tasks')
def tasks():
    return render_template("tasks.html")

@app.route('/settings')
def settings():
    return render_template("settings.html")

if (__name__== "__main__"):
  app.run(debug=True)