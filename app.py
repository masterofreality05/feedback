from models import app, connect_db, db, User, bcrypt, Feedback
from flask import render_template, flash, redirect, session
from forms import RegisterForm, Loginform, feebackCreator
from sqlalchemy.exc import IntegrityError

app.app_context().push()

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///twitter"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
connect_db(app)
db.create_all()

@app.route("/")
def show_home():
    """view function to retrieve and show our homepage"""
    if "user_id" in session:

        user_id = session["user_id"]
        return redirect(f"/users/{user_id}")
    else:
        return redirect("/register")
    

@app.route("/register", methods=["GET","POST"])
def show_handle_register():
    """view function to show our registration page and handle submission"""
    form = RegisterForm()

    if form.validate_on_submit():
        
        data = {k : v for (k,v) in form.data.items()}
        encrypted = User.register(data['password'])
        user = User(username=data['username'], password=encrypted, first_name=data['first_name'], last_name=data['last_name'])
        db.session.add(user)#
        try:
           db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username already taken, please choose another")
            return render_template("register.html", form=form)
        flash("successfully registered a new user","success")
        session["user_id"] = user.username
        return redirect("/")

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET","POST"])
def show_and_handle_login():
    """a view function to show our login form and handle submission"""
    form = Loginform()
    if form.validate_on_submit():
        #our post request will be filled in here 
        
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        if user:
            session["user_id"] = user.username
            flash(f"Login of {user.username} successfull","success")
            return redirect("/")


            #lets turn our bcrypt checker into a class method to keep our view clean
            #now we checked if login values are correct
            
        flash("Username or password not recognised","danger")

   
    return render_template("login.html", form=form)

@app.route("/secret")
def show_secret_page():
    """a view function that will show a secret html for logged in users"""
    if "user_id" in session:
       return redirect(f"/users/{session['user_id']}")
    else:
        return redirect("/")
    
@app.route("/users/<input>")
def show_user_details(input):
     """a view function to show details of the user after login  (logged in homepage)"""
   
     user = User.query.filter(User.username == input).first()
     form = feebackCreator()
     return render_template("user.html", user=user, form=form)
    
         
        
     
@app.route("/feedback", methods=["POST"])
def submit_feedback():
    """a function to post feedback to db and render in the homepage"""
    form = feebackCreator()
    if form.validate_on_submit():
        title = form.title.data
        content =form.content.data
        username = session["user_id"]
        
        feedback = Feedback(title=title, content=content, username=username)
        db.session.add(feedback)
        db.session.commit()
        flash("sucessfully added new feedback", "success")
        return redirect(f"/users/{username}")
   
    

@app.route("/logout", methods=["POST"])
def logout_route():
    """a route to handle a logout via post to prevent autoload"""
    session.pop("user_id")
    flash("You have successfully logged out", "danger")
    return redirect("/")

@app.route("/users/feedback/<int:id>/<method>", methods=["GET","POST"])
def handle_crud_feedback(id, method):
    """a route to handle edit and delete of feedback items"""
    if method == "delete":
        feedback = Feedback.query.get_or_404(id)
        user = feedback.user.username
        print(feedback)
        db.session.delete(feedback)
        db.session.commit()
        flash("Feeback successfully deleted","success")
        return redirect(f"/users/{user}")
    if method == "edit":

        form = feebackCreator()
        feedback = Feedback.query.get_or_404(id)
        user = feedback.user.username
        if form.validate_on_submit():
            feedback = Feedback.query.get_or_404(id)
            feedback.title = form.title.data
            feedback.content = form.content.data
            db.session.commit()
            flash("successfully updated post","success")
            return redirect(f"/users/{user}")
        print("do something")
        return render_template("editfeedback.html", form=form, feedback=feedback)

@app.route("/delete/<user_id>", methods=["GET","POST"])
def delete_user(user_id):
    """view function to delete user"""
    if user_id == session["user_id"]:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        session.pop("user_id")
        flash ("user successfully deleted","success")
        return redirect("/")
    else:
        flash("you are not permitted to delete this user","danger")
        return redirect(f"users/{user_id}")

    



#Add a new piece of feedback and redirect to /users/<username> — Make sure that only the user who is logged in can successfully add feedback
#GET /feedback/<feedback-id>/update
#Display a form to edit feedback — **Make sure that only the user who has written that feedback can see this form **
#POST /feedback/<feedback-id>/update
#Update a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written that feedback can update it
#POST /feedback/<feedback-id>/delete
#Delete a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written that feedback can delete it



