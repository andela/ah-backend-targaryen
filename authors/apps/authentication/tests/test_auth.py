# tests for authentication application
from authors.apps.authentication.models import User, UserManager
from authors.apps.authentication.views import (
    generate_ver_token, send_verification_link
    )
from rest_framework import serializers, status
from authors.apps.authentication.tests import BaseTestCase


class ModelTestCase(BaseTestCase):
    """Class with tests to do with registration model"""

    def test_registration_of_user(self):
        """Test that a user can register a new account."""
        self.new_count = User.objects.count()
        self.assertNotEqual(self.old_count, self.new_count)

    def test_registration_with_no_username(self):
        """Test that a user can not register wihtout a username."""
        self.assertRaises(TypeError, lambda: User.objects.create_user(
            username=None, email="david@gmail.com", password="password"))

    def test_registration_less_than_eight_characters(self):
        """Test that a user can not register wihtout a password."""
        self.assertRaises(TypeError, lambda: User.objects.create_user(
            username="david", email=None, password="password"))

    def test_registration_of_super_user(self):
        """Test that user can be registered as a super user"""
        self.assertRaises(TypeError, lambda: User.objects.create_superuser(
            username="davidsuper",
            email="davidsuper@gmail.com", password=None))

    def test_get_user_email(self):
        """ Test model method to get user's email """
        email = self.second_user.__str__()
        self.assertEqual(email, "david@gmail.com")

    def test_get_short_name(self):
        """ Test model method to get username """
        short_name = self.second_user.get_short_name()
        self.assertEqual(short_name, "david")

    def test_get_full_name(self):
        """ Test property to get username """
        full_name = self.second_user.get_full_name
        self.assertEqual(full_name, "david")


class ViewTestCase(BaseTestCase):
    """Class with tests to do with registration views"""

    def test_api_can_create_a_user(self):
        """Test the api has user creation capability."""
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)

    def test_register_with_an_existing_email(self):
        """Tests that user will not be created with an exisiting email"""
        response = self.client.post(
            '/api/users/', self.user_existing_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_an_invalid_email(self):
        """Tests that user will not be created with an invalid email"""
        response = self.client.post(
            '/api/users/', self.user_invalid_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_missing_password(self):
        """Tests that a user will not be created with a missing password"""
        response = self.client.post(
            '/api/users/', self.user_missing_password, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_missing_email(self):
        """Tests that a user will not be created with a missing email"""
        response = self.client.post(
            '/api/users/', self.user_missing_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_missing_name(self):
        """Tests that a user will not be created with a missing name"""
        response = self.client.post(
            '/api/users/', self.user_missing_name, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_non_alphanumeric_password(self):
        """Tests that a user will not be created with a missing name"""
        response = self.client.post(
            '/api/users/', self.user_non_alphanumeric_password, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_username_length_less_than_four(self):
        """Tests that user will not be created with
        an a username of length less than four characters
        """
        response = self.client.post(
            '/api/users/', self.user_username_less_than_four, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_with_password_length_less_than_eight(self):
        """Tests that user will not be created with a
        password of length less than eight characters """
        response = self.client.post(
            '/api/users/', self.user_password_less_than_eight, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_send_link_to_email(self):
        """Tests that a user can receive an email with token"""
        response = self.client.post(
            '/api/users/password_reset/', self.user_forgotten_password, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_password(self):
        """Tests that a user can update their password"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.put(
            '/api/users/password_update/', self.user_update_password, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_wrong_credentials_for_update_password(self):
        """Tests that a user can update their password"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'wrong123token')
        response = self.client.put(
            '/api/users/password_update/', self.user_update_password, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_does_not_exist_for_update_password(self):
        """Tests that a user can update their password"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.non_existing_user_token)
        response = self.client.put(
            '/api/users/password_update/', self.no_such_user_update_password, format="json")
        self.assertIn("No user was found", str(response.data))

    def test_login_a_user(self):
        """ Test login a registered user """
        response = self.client.post(
            '/api/users/login/', self.login_details, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_login_with_wrong_password(self):
        """ Test login with wrong password """
        response = self.client.post(
            '/api/users/login/', self.login_wrong_password, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_wrong_email(self):
        """ Test login with wrong email """
        response = self.client.post(
            '/api/users/login/', self.login_wrong_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_invalid_email(self):
        """ Test login with invalid email """
        response = self.client.post(
            '/api/users/login/', self.login_invalid_email, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_token_received_on_registration(self):
        """Tests that user will receive a token on successfil registration"""
        response = self.client.post(
            '/api/users/', self.user_data_token, format="json")
        self.assertEqual(self.response.status_code, status.HTTP_201_CREATED)
        assert "auth_token" in response.data

    def test_token_received_on_login(self):
        """Tests that user will receive a token on successfil login"""
        response = self.client.post(
            '/api/users/login/', self.login_details_token, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert "auth_token" in response.data

    def test_send_email_on_registration(self):
        token = generate_ver_token(self.user_data['user']['email'], 60)
        res = send_verification_link(self.user_data['user']['email'], token)
        self.assertEqual(res.status_code, status.HTTP_202_ACCEPTED)


class ValidatorsTestCase(BaseTestCase):
    """Class tests the validators used in the validate method"""

    def test_validator_for_username(self):
        """Test the validator for username less than four characters"""
        
        self.assertRaises(
            serializers.ValidationError,
            lambda: self.validator.is_username_valid(
                self.user['user']['username']))

    def test_validator_for_email(self):
        """Test the validator for invalid email"""
        self.assertRaises(
            serializers.ValidationError,
            lambda: self.validator.is_email_valid(
                self.user['user']['email']))

    def test_validator_for_password_length(self):
        """Test the validator for password less than eight characters"""
        self.assertRaises(
            serializers.ValidationError,
            lambda: self.validator.is_password_valid(
                self.user['user']['password1']))

    def test_validator_for_password_alphanumeric(self):
        """Test the validator for non alphanumeric password"""
        self.assertRaises(
            serializers.ValidationError,
            lambda: self.validator.is_password_valid(
                self.user['user']['password2']))
