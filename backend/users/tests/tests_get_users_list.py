from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User
from .for_tests import registrate_user, activate_user, get_auth_header


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

signup_data2 = {
    'first_name': 'Lexa',
    'surname': 'Bubnov',
    'username': 'Lak',
    'email': 'Lexa86@bk.ru',
    'password': '123456789',
    'password2': '123456789'
    }


class UsersListTests(APITestCase):

    url = reverse('users:users_list')

    def setUp(self):
        """Registrate, activate and login first user."""
        response = registrate_user(self, signup_data)
        user = User.objects.get(username=response.data['username'])
        activate_user(self, user)

    def test_get_user_list_with_one_user(self):
        """Tests getting list of users with only one user."""
        auth_header = get_auth_header(self, login_data)
        self.client.credentials(HTTP_AUTHORIZATION=auth_header)
        response = self.client.get(self.url)
        data = response.data
        self.assertEqual(data, [
                                {
                                    'first_name': 'Sasha',
                                    'surname': 'Kurkin',
                                    'username': 'Luk'
                                },
                                ])

    def test_get_user_list_wiht_some_users(self):
        """Tests getting list of users with more than one user."""
        response = registrate_user(self, signup_data2)
        user = User.objects.get(username=response.data['username'])
        activate_user(self, user)

        auth_header = get_auth_header(self, login_data)
        self.client.credentials(HTTP_AUTHORIZATION=auth_header)
        response = self.client.get(self.url)
        data = response.data
        self.assertEqual(data, [
                                {
                                    'first_name': 'Lexa',
                                    'surname': 'Bubnov',
                                    'username': 'Lak'
                                },
                                {
                                    'first_name': 'Sasha',
                                    'surname': 'Kurkin',
                                    'username': 'Luk'
                                },
                                ])

    def test_get_user_list_for_not_auth_user(self):
        response = self.client.get(self.url,)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
