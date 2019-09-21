from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from profiles.models import UserProfile


class ProfileViewsTest(APITestCase):
    # fixtures = ['quran.json']

    def setUp(self):
        """Create a dummy test user."""
        self.user = UserProfile.objects.create_user(
                'testuser', email='testuser@test.com', password='testpass')
        self.user.save()

    def test_post_user_ayah(self):
        """Test if a POST request to increment a read ayah works."""
        self.client.force_authenticate(user=self.user)
        self.assertTrue(self.user.is_authenticated, "User is not authenticated.")
        request = {'surah': 1, 'ayah': 1}
        response = self.client.post(reverse('user_ayah'), request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED,
                         msg="Response returned:\n{}".format(response.data))
        self.assertEqual(response.get('count'), 0)
        self.assertContains(response, 'user', status_code=status.HTTP_201_CREATED)
        self.assertContains(response, 'ayah', status_code=status.HTTP_201_CREATED)
        self.assertContains(response, 'count', status_code=status.HTTP_201_CREATED)

    def test_get_user_ayah(self):
        self.client.force_authenticate(user=self.user)
        self.assertTrue(self.user.is_authenticated, "User is not authenticated")
        response = self.client.get(reverse('user_ayah'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print("Response:\n{}".format(response.data))
