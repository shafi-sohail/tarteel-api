from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

search_json_request = {
    'arabicText': u'لقد خلقنا الانسان في كبد ',
    'translation': 'en-hilali',
}

search_json_response = {'result': {
    "queryText": "لقد خلقنا الانسان في كبد ",
    "matches": [{
        "surahNum": 90, "ayahNum": 4, "translationSurahName": "Al-Balad",
        "arabicSurahName": "سورة الـبلد",
        "translationAyah": "Verily, We have created man in toil.",
        "arabicAyah": "لَقَدْ خَلَقْنَا الْإِنْسَانَ فِي كَبَدٍ"
    }],
    "matchedTerms": ["لقد",  "خلقنا",  "الانسان", "في", "كبد", ""],
    "suggestions": []}
}

translation_json_request = {
    "ayahs": [{
        "surahNum": 90, "ayahNum": 4, "translationSurahName": "Al-Balad",
        "arabicSurahName": "سورة الـبلد", "translationAyah": "Verily, We have created "
        "man in toil.", "arabicAyah": "لَقَدْ خَلَقْنَا الْإِنْسَانَ فِي كَبَدٍ"
        }],
    "translation": "en-hilali"
}

translation_json_response = {
    "result": [{
        "surahNum": 90, "ayahNum": 4, "translationSurahName": "Al-Balad",
        "arabicSurahName": "سورة الـبلد", "translationAyah": "Verily, We have created "
        "man in toil.", "arabicAyah": "لَقَدْ خَلَقْنَا الْإِنْسَانَ فِي كَبَدٍ"
        }]
}


class IqraTestCase(APITestCase):
    def test_search(self):
        url = reverse('iqra-search')
        response = self.client.post(url, search_json_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             search_json_response)

    def test_translation(self):
        url = reverse('iqra-translation')
        response = self.client.post(url, translation_json_request, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertJSONEqual(str(response.content, encoding='utf8'),
                             translation_json_response)

