# -*- coding: utf-8 -*-
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .Iqra import Iqra


@api_view(['POST'])
def getSearchResult(request):
    """Returns the result of a search. Parameters need to be JSON in the body
    Example: /api/search
    JSON: {
        'arabicText': u'محمد',
        'translation': 'en-hilali',
    }
    :param request: REST API request object.
    :type request: rest_framework.request.Request
    :return: JSON response with query text, matches, and suggestions
    :rtype: JsonResponse
    """
    data = request.data
    value = data['arabicText']
    if 'translation' in data:
        translation = data['translation']
    else:
        translation = 'en-hilali'
    iqra = Iqra()
    result = iqra.getResult(value, translation)
    result = {'result': result}
    return JsonResponse(result)


@api_view(['POST'])
def getAyahTranslations(request):
    """Returns the translations of an ayah. Parameters need to be JSON in the body
    Example: /api/translations
    JSON: {
        'ayahs': [Ayahs(surahNum, ayahNum)],
        'translation': 'en-hilali',
    }
    :param request: REST API request object.
    :type request: rest_framework.request.Request
    :return: JSON response with query text, matches, and suggestions
    :rtype: JsonResponse
    """
    data = request.data
    ayahs = data['ayahs']
    if 'translation' in data:
        translation = data['translation']
    else:
        translation = 'en-hilali'
    iqra = Iqra()
    result = iqra.getTranslations(ayahs, translation)
    result = {'result': result}
    return JsonResponse(result)
