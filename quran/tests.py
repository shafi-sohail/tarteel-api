from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from quran.views import TranslationViewSet


class QuranTestCase(APITestCase):
    def test_search(self):
        factory = APIRequestFactory()
        view = TranslationViewSet.as_view({'get': 'list'})
        request = factory.get(reverse('translation-list'))
        response = view(request)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertContains(response, 'next')

