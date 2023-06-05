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
        return redirect(f"/users/{session['user_id']}")
    else:
        return redirect("/register")
    
@app.route("/register", methods=["GET","POST"])
def show_handle_register():
    """view function to show our registration page and handle submission"""
    form = RegisterForm()

    if form.validate_on_submit():
        user = User()
        encrypted = User.register(form.password.data)
        
        form.populate_obj(user)
        user.password = encrypted
        db.session.add(user)

        try:
           db.session.commit()
        except IntegrityError:
            form.username.errors.append("Username already taken, please choose another")
            return render_template("register.html", form=form)
        
        flash("successfully registered a new user","success")
        session["user_id"] = user.username
        return redirect("/")

    return render_template("register.html", form=form)

@app.route("/tweets")
def show_all_tweets():
    """view function to show all tweets"""
    tweets = Feedback.query.all()
    user = User.query.get(session['user_id'])
    return render_template("tweets.html", tweets=tweets, user=user)


@app.route("/login", methods=["GET","POST"])
def show_and_handle_login():
    """a view function to show our login form and handle submission"""
    form = Loginform()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = User.authenticate(username, password)
        if user:
            session["user_id"] = user.username
            flash(f"Login of {user.username} successfull","success")
            return redirect("/")
            
        flash("Username or password not recognised","danger")
    return render_template("login.html", form=form)

    
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
      
        username = session["user_id"]
        feedback = Feedback()
        form.populate_obj(feedback)
        feedback.username = username
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

    feedback = Feedback.query.get_or_404(id)
    user = feedback.user
    if session['user_id'] == user.username or user.is_admin == True:
        if method == "delete":
         db.session.delete(feedback)
         db.session.commit()
         flash("Feeback successfully deleted","success")
         return redirect(f"/users/{user.username}")
    
        if method == "edit":
            form = feebackCreator()
            if form.validate_on_submit():
                form.populate_obj(feedback)
                db.session.commit()
                flash("successfully updated post","success")
                return redirect(f"/users/{user.username}")
    
            return render_template("editfeedback.html", form=form, feedback=feedback)
    else:
        flash("you are not authorized to do that", "danger")

        return redirect("/tweets")
    

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