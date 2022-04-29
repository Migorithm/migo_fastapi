import unittest
from fastapi.testclient import TestClient
from main import app

class TestAuth(unittest.TestCase):
    #Fixtures
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = TestClient(app)
        
    def tearDown(self) -> None:
        self.app.cookies.clear()
    
    
    
    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(200,response.status_code)
        self.assertEqual({"msg":"Hello World"},response.json())
    
    def test_login_get(self):
        response=self.app.get('/login')
        self.assertEqual(200,response.status_code)
        
        
    def test_login_post(self):
        response = self.app.post('/login',data={"username":"migo","password":"admin1234"}) #form must be given into a data, not json
  
        self.assertEqual(302,response.status_code)
        
    def test_access_to_protected(self):
        response = self.app.get('/protected')
        self.assertEqual(401,response.status_code) #Unauthorized!
    
        
        self.test_login_post() #Login 
        response = self.app.get('/protected') #And try
        self.assertEqual(200,response.status_code)
        self.assertEqual({"a":"b"},response.json())
    
    def test_logout(self):
        response = self.app.get('/logout') #Logout without login.
        self.assertEqual(401,response.status_code) #unauthorized
        
        self.test_login_post() #Login 
        response = self.app.get('/logout')
        self.assertEqual(200,response.status_code)  #redirection code is temporary -- the actual code you get is the status_code from final destination
        print("dd")
        self.assertEqual('None',self.app.cookies.get_dict().get("AUTH"))
        
        
    def test_registration(self):
        #valid request with unexisting id
        user_data = {"name":"mago","password":"admin1234"} #Pydantic schema
        register_res = self.app.post('/register',data=user_data)
        self.assertEqual(302,register_res.status_code)
        
        
        user_data = {"username":"mago","password":"admin1234"} #OAuth schema
        login_res = self.app.post('/login',data=user_data)
        self.assertEqual(302,login_res.status_code)
        
        self.app.cookies.clear()
        
        #Invalid request with already existing username
        user_data = {"name":"mago","password":"admin1234"} #Pydantic schema
        register_res = self.app.post('/register',data=user_data)
        self.assertEqual(400,register_res.status_code)


if __name__ =="__main__":
    unittest.main()