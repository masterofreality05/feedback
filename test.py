import unittest
from app import app
from flask import session
from models import app, connect_db, db, User, Feedback



app.config["WTF_CSRF_ENABLED"] = False

class TestSimpleRoutes(unittest.TestCase):

    def setUp(self):
        """do this before each test"""
     
    
    def tearDown(self):
        """do this after every test"""
   
    def test_homepage_logged_out(self):
        """unit testing to test the correct returned html markup"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session.clear()
        res = client.get("/", follow_redirects=True)
        html = res.get_data(as_text=True)
        self.assertEqual(res.status_code,200)
        self.assertIn("register-user-form", html)
    
    def test_homepage_logged_in(self):
        """unit testing to test the correct returned html markup"""
        with app.test_client() as client:
            with client.session_transaction() as test_session:
                test_session['user_id'] = "d"
            res = client.get("/", follow_redirects=True)
            html = res.get_data(as_text=True)
                
            self.assertEqual(res.status_code,200)
            self.assertIn("Create", html) 
            self.assertEqual(test_session['user_id'], "d")
        
    def test_login(self):
        """integration test to validate login process"""
        with app.test_client() as client:
            test_data = {"username":"d","password":"d"}
            res = client.post("/login", data={k:v for (k,v) in test_data.items()},
                                                     follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Login of d successfull", html)
            session.pop("user_id")
    
    def test_user_view(self):
        """unit test to test view for individual user"""
        with app.test_client() as client:
            user_id = "u"
            user = User.query.filter(User.username == user_id).first()
            res = client.get(f"/users/{user.username}")
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code,200)
            self.assertIn("uganda", html)

    def test_user_creation(self):
        with app.test_client() as client:
            test_data = {"username": "test_register", "password":"quuwu", "first_name":"mctest",
                         "last_name":"testlast", "is_admin": True}
          
            form_object = {k:v for (k,v) in test_data.items()}
            res = client.post("/register", data={k:v for (k,v) in form_object.items()},
                                                     follow_redirects=True)
            html = res.get_data(as_text=True)
           # self.assertEqual(res.status_code, 200)
            #self.assertIn("successfully registered a new user", html)
            user = User.query.get("test_register")
            db.session.delete(user)
            db.session.commit() 

class TestAuthorizedPaths(unittest.TestCase):
         def test_authorized_feedback_creation(self):  
            with app.test_client() as client:
                with client.session_transaction() as session:
                   session['user_id'] = "u"
            
            test_data = {"title": "test_feedback1", "content":"quuwu1"}
            form_object = {k:v for (k,v) in test_data.items()}
            
            res = client.post("/feedback", data={k:v for (k,v) in form_object.items()},
                                                     follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("sucessfully added new feedback", html)
            print("---------------", html)
            session.pop("user_id")
            feedback = Feedback.query.get("test_feedback1")
            db.session.delete(feedback)
            db.session.commit()
   

    
