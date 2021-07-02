from django.http import response
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ed.models import Branch
from users.models import NewUser

class PostTestS(APITestCase):
    def test_view_posts(self):
        url = reverse('eduvy_api:listcreate')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)