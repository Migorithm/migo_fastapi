import unittest
from fastapi.testclient import TestClient
from main import app
from routers.auth import authenticate_user


class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)
        cls.mock_client_data = [
            {"username": "migo","password":"admin1234"},
            {"username": "maago","password":"admin1234"}]
    
    
    def tearDown(self) -> None:
        self.client.cookies.clear()
    
    def test_login(self) -> None:
        for client in self.mock_client_data[:1]:
            username = client.get("username")
            password = client.get("password")
            with self.subTest(username=username,password=password):
                self.assertEqual(authenticate_user(username,password), True)
                
        response = self.client.get('/login')
        self.assertEqual(200, response.status_code)
    
    
    def test_login_post(self):
        for client in self.mock_client_data:
            with self.subTest(client=client):
                print(client)
                response2 = self.client.post('/login',data=client)
                self.assertEqual(302, response2.status_code)
        
            

if __name__ == "__main__":
    unittest.main()