# tests for authentication application
from django.test import TestCase
from authors.apps.authentication.models import User, UserManager
from rest_framework.test import APIClient
from rest_framework import status

class ModelTestCase(TestCase):
    """Class with tests to do with registration model"""
    def setUp(self):
        """Define the test client and test variables"""
        self.old_count = User.objects.count()
        self.user = User.objects.create_user(username="david", email="david@gmail.com", password="password")
        # self.user_manager = UserManager(username="david", email="david@gmail.com", password="password")
    
    def test_registration_of_user(self):
        """Test that a user can register a new account."""
        self.new_count = User.objects.count()
        self.assertNotEqual(self.old_count, self.new_count)
    
    def test_registration_with_no_username(self):
        """Test that a user can not register wihtout a username."""
        self.assertRaises(TypeError, lambda: User.objects.create_user(username=None, email="david@gmail.com", password="password"))
    
    def test_registration_less_than_eight_characters(self):
        """Test that a user can not register wihtout a password."""
        self.assertRaises(TypeError, lambda: User.objects.create_user(username="david", email=None, password="password"))
    
    def test_registration_of_super_user(self):
        """Test that user can be registered as a super user"""
        self.assertRaises(TypeError, lambda: User.objects.create_superuser(username="davidsuper", email="davidsuper@gmail.com", password=None))

class ViewTestCase(TestCase):
    """Class with tests to do with registration views"""
    def setUp(self):
        """Test registration api views"""
        self.client = APIClient()
        self.user_data = {"user":{"username":"samuel", "email":"samuel@gmail.com", "password":"password"}}
        self.user_existing_email = {'user':{'username':'samuel', 'email':'samuel@gmail.com', 'password':'password'}}
        self.user_missing_password = {'user':{'username':'baron', 'email':'baron@gmail.com', 'password':None}}
        self.user_missing_email = {'user':{'username':'samuel', 'email':None, 'password':'password'}}
        self.user_missing_name = {'user':{'username':None, 'email':'bridget@gmail.com', 'password':'password_bridget'}}

        self.response = self.client.post('/api/users/',self.user_data,format="json")
        
    def test_api_can_create_a_user(self):
        """Test the api has user creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
    
    def test_register_with_an_existing_email(self):
        """Tests that user will not be cfreated with an exisiting email"""
        response = self.client.post('/api/users/',self.user_existing_email,format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_with_missing_password(self):
        """Tests that a user will not be created with a missing password"""
        response = self.client.post('/api/users/',self.user_missing_password,format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_with_missing_email(self):
        """Tests that a user will not be created with a missing email"""
        response = self.client.post('/api/users/',self.user_missing_email,format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_with_missing_name(self):
        """Tests that a user will not be created with a missing name"""
        response = self.client.post('/api/users/',self.user_missing_name,format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

