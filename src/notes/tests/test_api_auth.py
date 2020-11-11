from django.urls import reverse
from rest_framework import status
from parameterized import parameterized

from commons.random import generate_strong_password
from commons.tests import APITestCase
from mixer.backend.django import mixer


class AuthAPITestCase(APITestCase):

    def test_should_sign_up(self):
        # Arrange
        password = generate_strong_password()

        # Act
        response = self.client.post(reverse('api:auth-sign-up'), data={
            'name': self.faker.name(),
            'email': self.faker.email(),
            'password': password,
            'password_confirm': password
        })

        # Assert
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)

        # data = response.json()

        # self.assertSchema(schema, data)
    
    def test_repeat_email(self):
        # Arrange
        password = generate_strong_password()
        user = mixer.blend('notes.User')

        # Act
        response = self.client.post(reverse('api:auth-sign-up'), data={
            'name': self.faker.name(),
            'email': user.email,
            'password': password,
            'password_confirm': password
        })

        # Assert
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)

    @parameterized.expand([
        'invalid_email', '', (None, )
    ])
    def test_email_not_valid(self, email):
        # Arrange
        password = generate_strong_password()
        payload = {
            'name': self.faker.name(),
            'email': email,
            'password': password,
            'password_confirm': password
        }

        # Act
        response = self.client.post(reverse('api:auth-sign-up'), data={
            key: val for key, val in payload.items() if val is not None
        })

        # Assert
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
