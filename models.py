from flask import Flask
from flask_bcrypt import Bcrypt 
from flask_sqlalchemy import SQLAlchemy

def connect_db(app):
    """Connect to database."""
    db.app = app
    db.init_app(app)


app = Flask(__name__)
db = SQLAlchemy()
bcrypt = Bcrypt()


class User(db.Model):
    """user model for our database"""

    __tablename__ = "users"

    username = db.Column(db.String(20),
                         primary_key=True,
                         unique=True,
                         nullable=False)
    
    password = db.Column(db.Text,
                         nullable=False)
    
    first_name = db.Column(db.String(30),
                        nullable=False)
    
    last_name = db.Column(db.String(30),
                        nullable=False)
    
    @classmethod
    def register(cls,password):
        """registering user w/hashed password and return user object"""
        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user w/username and hashed pwd
        return hashed_utf8
    
    @classmethod
    def authenticate(cls, username, password):
        """a method on our class to provide authentication provided by username and password"""
        user = User.query.filter(User.username == username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False
        
class Feedback(db.Model):
    """model for our feeback"""

    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, 
                   primary_key=True,
                   autoincrement=True)
    
    title = db.Column(db.String(100),
                      nullable=False)
    content = db.Column(db.Text,
                        nullable=False)
    username = db.Column(db.ForeignKey('users.username'))

    user = db.relationship('User', backref="feedbacks")





