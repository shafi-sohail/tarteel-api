# -*- coding: utf-8 -*-
import logging

from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from rest_framework.decorators import api_view

from .iqra import Iqra

logger = logging.getLogger('django')


@api_view(['POST'])
def get_search_result(request):
    """Returns the result of a search with a specified translation and query limit.
    Example: /api/search
    JSON: {
        'arabicText': u'محمد',
        'translation': 'en-hilali',
        'limit': 5
    }
    :param request: REST API request object.
    :type request: rest_framework.request.Request
    :return: JSON response with query text, matches, and suggestions
    :rtype: JsonResponse
    """
    logger.info("IQRA: Search request")
    data = request.data
    value = data.get('arabicText', None)
    translation = data.get('translation', 'en-hilali')
    limit = data.get('limit', None)
    if value is None:
        return HttpResponseBadRequest("Missing 'arabicText' field.")
    iqra = Iqra()
    result = iqra.get_result(value, translation, limit)
    result = {'result': result}
    return JsonResponse(result)


@api_view(['POST'])
def get_ayah_translations(request):
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
    translation = data.get('translation', 'en-hilali')
    ayahs = data.get('ayahs', None)
    if ayahs is None:
        return HttpResponseBadRequest("Missing 'ayahs' field.")
    iqra = Iqra()
    result = iqra.get_translations(ayahs, translation)
    result = {'result': result}
    return JsonResponse(result)
