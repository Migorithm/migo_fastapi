from fastapi.testclient import TestClient
import unittest
from main import app




class TestFastAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.app = TestClient(app)
        
    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(200,response.status_code)
        self.assertEqual({"msg":"Hello World"},response.json())
    
    def test_item_get(self):
        response = self.app.get('/items/foo',headers={"X-Token":"coneofsilence"})
        self.assertEqual(200,response.status_code)
        self.assertEqual({"id":"foo","title":"Foo","description":"There goes my hero"},response.json())
    
    def test_item_post(self):
        response = self.app.post("/items/",
        headers={"X-Token": "coneofsilence"},
        json={"id": "foobar", "title": "Foo Bar", "description": "The Foo Barters"},
        )
        self.assertEqual(200,response.status_code)
        self.assertEqual({
            "id": "foobar",
            "title": "Foo Bar",
            "description": "The Foo Barters"},response.json())

if __name__ =="__main__":
    unittest.main()