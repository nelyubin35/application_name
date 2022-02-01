from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from users.models import User
from services_for_tests.for_tests import registrate_user, activate_user, login_user, get_auth_headers, set_auth_headers

signup_data = {
    'first_name': 'Sasha',
    'surname': 'Kurkin',
    'username': 'Luk',
    'email': 'nepetr86@bk.ru',
    'password': '123456789',
    'password2': '123456789'
}

login_data = {
    'username': 'Luk',
    'password': '123456789'
}


class ChangePasswordTests(APITestCase):
    """Class for testing changing password."""

    url = reverse('users:change_user_password')
    data = {
        'old_password': '123456789',
        'new_password': '1234567890',
        'new_password2': '1234567890',
        }

    def setUp(self):
        """Registrate, activate user."""
        response = registrate_user(self, signup_data)
        user = User.objects.get(username=response.data['username'])
        activate_user(self, user)

    def test_change_password(self):
        """
        Tests changing password.
        Checks that password was changed, auth token was deleted.
        Checks that users can log in with new password.
        """
        token, signature = get_auth_headers(self, login_data)
        set_auth_headers(self, token, signature)
        response = self.client.put(self.url, data=self.data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.__check_that_password_was_changed_successfully()
        self.__check_successfully_login_with_new_password(token)

    def __check_that_password_was_changed_successfully(self):
        """
        Checks that password was changed
        correctly and auth token was deleted.
        """
        user = User.objects.get(username="Luk")
        self.assertEqual(user.check_password(
                         self.data['old_password']), False)
        self.assertEqual(user.check_password(
                         self.data['new_password']), True)
        with self.assertRaises(Token.DoesNotExist):
            Token.objects.get(user=user)

    def __check_successfully_login_with_new_password(self, user_auth_token):
        """Check that user can log in with new password."""
        new_login_data = {
            'username': 'Luk',
            'password': '1234567890',
            }
        self.client.credentials()
        response = login_user(self, new_login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_user_auth_token = response.data['token']
        self.assertNotEqual(user_auth_token, new_user_auth_token)

    def test_new_password_not_equal_new_password2(self):
        """
        Tests changing password when input data not correct.
        new password != new password2.
        """
        data = {
            'old_password': '123456789',
            'new_password': 'first_password',
            'new_password2': 'second_password'
            }

        token, signature = get_auth_headers(self, login_data)
        set_auth_headers(self, token, signature)
        response = self.client.put(self.url, data=data,
                                   format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_new_password(self):
        """
        Tests changing password on password
        witch length smaller than 8 chars.
        """
        data = {
            'old_password': '123456789',
            'new_password': 'short',
            'new_password2': 'second_password',
            }

        data2 = {
            'old_password': '123456789',
            'new_password': 'first_password',
            'new_password2': 'short',
            }

        token, signature = get_auth_headers(self, login_data)
        set_auth_headers(self, token, signature)

        response = self.client.put(self.url, data=data,
                                   format='json')
        response2 = self.client.put(self.url, data=data2,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
