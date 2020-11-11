from commons.tests import AuthenticatedAPITestCase
from mixer.backend.django import mixer
from rest_framework import status
from django.urls import reverse


class NotesAPITestCase(AuthenticatedAPITestCase):
    note_schema = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "content": {"type": ["string", "null"]},
            "category": {
                "type": ["object", "null"],
                "properties": {
                    "id": {"type": "integer"},
                    "name": {"type": "string"},
                },
                "required": ["id", "name"],
                "additionalProperties": False
            },
            "archived": {"type": "boolean"},
            "created_at": {"type": "string", "format": "date-time"},
            "last_update": {"type": "string", "format": "date-time"}
        },
        "required": ["id", "title", "content", "category", "archived", "created_at", "last_update"],
        "additionalProperties": False
    }

    def test_should_list(self):
        # Arrange
        mixer.cycle(10).blend('notes.Note', user=self.user)

        # Act
        response = self.client.get(reverse('api:notes-list'))

        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(10, data['count'])

    def test_should_list_owner_notes(self):
        # Arrange
        unknown_user = mixer.blend('notes.User')

        notes = mixer.cycle(5).blend('notes.Note', user=self.user)
        unknown_notes = mixer.cycle(5).blend('notes.Note', user=unknown_user)

        # Act
        response = self.client.get(reverse('api:notes-list'))

        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)

        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(5, data['count'])

        note_ids = { obj.pk for obj in notes }
        self.assertTrue(all([item['id'] in note_ids for item in data['results']]))
    
    def test_should_not_list_if_not_auth(self):
        # Arrange
        mixer.cycle(10).blend('notes.Note', user=self.user)
        self.unauthenticated()

        # Act
        response = self.client.get(reverse('api:notes-list'))

        # Assert
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_should_list_by_category(self):
        # Arrange
        category1 = mixer.blend('notes.Category')
        category2 = mixer.blend('notes.Category')
        mixer.cycle(5).blend('notes.Note', user=self.user, category=category1)
        mixer.cycle(5).blend('notes.Note', user=self.user, category=category2)
        mixer.cycle(5).blend('notes.Note', user=self.user, category=None)

        # Act
        response = self.client.get(reverse('api:notes-list'), data={
            'category': category1.pk
        })

        # Assert
        self.assertEqual(status.HTTP_200_OK, response.status_code)
    
        data = response.json()

        self.assertPaginatedSchema(self.note_schema, data)
        self.assertEqual(5, data['count'])
        self.assertTrue(all([item['category']['id'] == category1.pk for item in data['results']]))
