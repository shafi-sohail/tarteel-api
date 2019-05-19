from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

demographic_json_request = {
    "platform": "web",
    "gender": "female",
    "age": "19",
    "ethnicity": "SY",
    "timestamp": "2018-08-06T06:30:46.823000Z",
    "qiraah": None
}

demographic_no_session_json_request = {
    "platform": "web",
    "gender": "female",
    "age": "19",
    "ethnicity": "SY",
    "timestamp": "2018-08-06T06:30:46.823000Z",
    "qiraah": None
}

demographic_no_session_json_response = {
    "session_id": [
        "This field is required."
    ]
}


class DemographicTestCase(APITestCase):
    def test_post_demographic(self):
        url = reverse('demographicinformation-list')
        response = self.client.post(url, demographic_json_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             demographic_json_request)

    def test_post_demographic_no_session(self):
        url = reverse('demographicinformation-list')
        response = self.client.post(url, demographic_no_session_json_request,
                                    format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             demographic_no_session_json_response)
