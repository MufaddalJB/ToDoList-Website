from datetime import datetime
from flask import Flask,render_template,request,redirect,url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager, login_required,logout_user
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config["SECRET_KEY"]="123456"
db = SQLAlchemy()
login_manager=LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def loader_user(user_id):
  user=User.query.get(int(user_id))
  return(user)

class User(db.Model,UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    email=db.Column(db.String(20),nullable=False )
    password=db.Column(db.String(80),nullable=False)
    name=db.Column(db.String(20),nullable=False )
    number=db.Column(db.String(20),nullable=False )
    age=db.Column(db.String(20),nullable=False )

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sno = db.Column(db.Integer)
    title = db.Column(db.String(20))
    description = db.Column(db.String(80))
    scheduled_datetime=db.Column(db.DateTime , default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('todos', lazy=True))

db.init_app(app)
with app.app_context():
    db.create_all()
    
@app.route("/")
def home():
    return render_template("welcome.html")

@app.route('/login',methods=["POST","GET"])
def login():
    if request.method=="POST":
        user=User.query.filter_by(email=request.form.get("email")).first()
        if user.password==request.form.get("password"):
            loader_user(user.id)
            session['user_id']=user.id
            return redirect(url_for("homeScreen"))
        else:
            return render_template("Login.html",error='Invalid User')
    return render_template("Login.html")

@app.route('/register', methods=["POST","GET"])
def register():
    if request.method == "POST":
        email = request.form.get("email") 
        password = request.form.get("password")
        name=request.form.get("name")
        number=request.form.get("number")
        age=request.form.get("age")
        
        if not email or not password:
            flash("Please provide both email and password.", "error")
            return redirect(url_for("register"))
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email is already in use. Please choose a different one.", "error")
            return redirect(url_for("register"))
        new_user = User(email=email, password=password,name=name,age=age,number=number) 
        db.session.add(new_user)
        db.session.commit()
        flash("Registration successful. You can now log in.", "success")
        return redirect(url_for("login"))    
    return render_template("register.html")

@app.route('/home')
def homeScreen():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template("home.html", user=user)
    return redirect(url_for("login"))

@app.route('/profile')
def profile():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template("profile.html", user=user)
    return render_template("profile.html")

@app.route('/tasks',methods=["Get","POST"])
def tasks():
    if 'user_id' in session:
        if request.method == "POST":
            title = request.form["title"]
            desc = request.form["description"]
            date_time=request.form['scheduled_datetime']
            scheduled_datetime = datetime.strptime(date_time, '%Y-%m-%dT%H:%M') 
            user_id = session['user_id']
            
            user = User.query.get(user_id)
            todo = Todo(title=title, description=desc,scheduled_datetime=scheduled_datetime, user=user)
            
            db.session.add(todo)
            db.session.commit()

        allTodo = Todo.query.filter_by(user_id=session['user_id']).all()
        user = User.query.get(session['user_id'])
        return render_template("tasks.html", allTodo=allTodo, user=user)
    
    return render_template("tasks.html")

@app.route("/update/<int:id>",methods=["GET","POST"])
def update(id):
    if request.method=="POST":
        title=request.form["title"]
        desc=request.form["description"]
        date_time=request.form['scheduled_datetime']
        scheduled_datetime = datetime.strptime(date_time, '%Y-%m-%dT%H:%M') 
        todo=Todo.query.get(id) 
        todo.title=title
        todo.description=desc
        todo.scheduled_datetime=scheduled_datetime
        db.session.add(todo)
        db.session.commit()
        return redirect("/tasks")
    user = User.query.get(session['user_id'])
    todo=Todo.query.get(id)
    return render_template("update.html",todo=todo,user=user)

@app.route('/delete/<int:id>')
def delete(id):
    if 'user_id' in session:
        todo= Todo.query.get(id)
        db.session.delete(todo)
        db.session.commit()
        return redirect("/tasks")
    return render_template("tasks.html")


@app.route('/settings')
def settings():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template("settings.html", user=user)
    return render_template("settings.html")

@app.route('/calendar')
def calendar():
    allTodo = Todo.query.filter_by(user_id=session['user_id']).all()
    user = User.query.get(session['user_id'])
    return render_template('calendar.html',user=user,allTodo=allTodo)

@app.route("/logout")

def logout():

    session.pop("user_id",None)
    return redirect(url_for("login"))

if (__name__== "__main__"):
    app.run(debug=True)
