from django.urls import reverse

from rest_framework.test import APITestCase
from rest_framework import status

from users.models import User, NotConfirmedEmail
from users.services.token_services import TokenService
from users.services.datetime_services import DatetimeService
from .for_tests import registrate_user, activate_user, get_auth_headers,\
                       set_auth_headers, ForTestsDateTimeService


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


class EmailConfirmationTests(APITestCase):
    """Class for tests changing user email"""

    new_user_email = 'tochno_ne_danil@mail.ru'

    def setUp(self):
        """Registrate, activate, login, and change user email."""
        response = registrate_user(self, signup_data)
        self.user = User.objects.get(username=response.data['username'])
        activate_user(self, self.user)

        changing_email_data = {
            'new_user_email': 'tochno_ne_danil@mail.ru'
        }
        changing_email_url = reverse('users:change_user_email')

        token, signature = get_auth_headers(self, login_data)
        set_auth_headers(self, token, signature)
        self.client.put(changing_email_url, data=changing_email_data,
                        format='json')


    def test_confirm_user_email(self):
        """
        Checks that user email was changed and his new
        email address was deleted from temporary list.
        """
        encrypted_datetime = DatetimeService.get_encrypted_datetime()
        token = TokenService.get_email_confirmation_token(
            self.user, encrypted_datetime, self.new_user_email)

        kwargs = {'id': self.user.id,
                  'encrypted_datetime': encrypted_datetime,
                  'token': token
                  }

        url = reverse('users:email_confirmation', kwargs=kwargs)
        response = self.client.get(url)
        user = User.objects.get()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(user.email, self.new_user_email)
        self.assertEqual(NotConfirmedEmail.objects.count(), 0)

    def test_confirm_user_email_with_overdue_token(self):
        """Tests confirm user email with overdue token."""
        encrypted_datetime = ForTestsDateTimeService.get_encrypted_datetime()
        token = TokenService.get_email_confirmation_token(
            self.user, encrypted_datetime, self.new_user_email)

        kwargs = {'id': self.user.id,
                  'encrypted_datetime': encrypted_datetime,
                  'token': token
                  }

        url = reverse('users:email_confirmation', kwargs=kwargs)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)







