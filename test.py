import unittest
from app import app
from models import app, connect_db, db, User
from forms import RegisterForm,Loginform


app.config["WTF_CSRF_ENABLED"] = False

class TestSimpleRoutes(unittest.TestCase):

    def setUp(self):
        """do this before each test"""
        test_user = User(username="test",first_name="testy", password="itsatest", last_name="tester", is_admin=True)
        db.session.add(test_user)
        db.session.commit()
    
    def tearDown(self):
        """do this after every test"""
        delete_test_user = User.query.get('test')
        if User.query.get("test_register"):
            tested_register_user = User.query.get("test_register")
            db.session.delete(tested_register_user)
        db.session.delete(delete_test_user)
        db.session.commit()

    def test_homepage_logged_out(self):
        """unit testing to test the correct returned html markup"""
        with app.test_client() as client:
            
            res = client.get("/", follow_redirects=True)
            html = res.get_data(as_text=True)
            
            self.assertEqual(res.status_code,200)
            self.assertIn("register-user-form", html)
    
    def test_homepage_logged_in(self):
        """unit testing to test the correct returned html markup"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = "d"
                res = client.get("/", follow_redirects=True)
                html = res.get_data(as_text=True)
                
                self.assertEqual(res.status_code,200)
                #self.assertIn("Create", html) # will bring up in the 1-1
                self.assertEqual(session['user_id'], "d")
    
    def test_login(self):
        """integration test to validate login process"""
        with app.test_client() as client:
            form = Loginform()
            form.username.data = "d"
            form.password.data = "d"
            res = client.post("/login", data={k:v for (k,v) in form.data.items()},
                                                     follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("Login of d successfull", html)

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
            form = RegisterForm()
            form.username.data = "test_register"
            form.password.data = "quuwu"
            form.first_name.data = "mctest"
            form.last_name.data = "testlast"
            form.is_admin.data = True
            form_object = {k:v for (k,v) in form.data.items()}
            print(form_object)

            res = client.post("/register", data={k:v for (k,v) in form.data.items()},
                                                     follow_redirects=True)
            html = res.get_data(as_text=True)
            self.assertEqual(res.status_code, 200)
            self.assertIn("successfully registered a new user", html)

            user = User.query.get("test_register")
            db.session.delete(user)
            db.session.commit()

        

        
   