
   



    
 


                
                
            

        

        
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

   