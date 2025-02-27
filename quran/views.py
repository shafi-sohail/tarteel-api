import random
# Django
from django_filters import rest_framework as filters
from django.forms.models import model_to_dict
# Django Rest Framework
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
# Quran app
from quran.models import Surah, Ayah, AyahWord, Translation
import quran.serializers


class SurahFilter(filters.FilterSet):
    """Filter surahs by name, number or ayah number."""
    ayah = filters.NumberFilter(field_name='ayah__verse_number')
    surah = filters.NumberFilter(field_name='number')
    name = filters.NumberFilter(field_name='name')

    class Meta:
        model = Surah
        fields = ['ayah', 'surah', 'name']


class SurahViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for surahs."""
    queryset = Surah.objects.all()
    serializer_class = quran.serializers.SurahSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = SurahFilter


class AyahFilter(filters.FilterSet):
    """Filter ayahs by sajdahs, surah or ayah numbers."""
    surah = filters.NumberFilter(field_name='chapter_id__number')
    ayah = filters.NumberFilter(field_name='verse_number')
    sajdah = filters.BooleanFilter(field_name='sajdah')

    class Meta:
        model = Ayah
        fields = ['surah', 'ayah', 'sajdah']


class AyahViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for ayahs."""
    queryset = Ayah.objects.all()
    serializer_class = quran.serializers.AyahSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AyahFilter

    @action(detail=False, methods=['get'])
    def random(self, request):
        # User tracking - Ensure there is always a session key.
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key

        ayah_count = Ayah.objects.count() - 1
        rand_index = random.randint(0, ayah_count)
        rand_ayah = Ayah.objects.all()[rand_index]
        surah_num = rand_ayah.chapter_id.number
        ayah_num = rand_ayah.verse_number
        words = AyahWord.objects.filter(ayah=rand_ayah, ayah__verse_number=ayah_num,
                                        ayah__chapter_id__number=surah_num)
        translations = Translation.objects.filter(ayah__verse_number=ayah_num,
                                                  ayah__chapter_id__number=surah_num)
        ayah_dict = model_to_dict(rand_ayah)
        ayah_dict['translations'] = list(translations.values())
        ayah_dict['words'] = list(reversed(words.values()))
        ayah_dict['session_id'] = session_key

        return Response(ayah_dict)


class AyahWordFilter(filters.FilterSet):
    """Filter words by surah, ayah, and word number."""
    surah = filters.NumberFilter(field_name='ayah__chapter_id__number')
    ayah = filters.NumberFilter(field_name='ayah__verse_number')
    number = filters.NumberFilter(field_name='number')

    class Meta:
        model = AyahWord
        fields = ['surah', 'ayah', 'number']


class AyahWordViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for an ayah's words."""
    queryset = AyahWord.objects.all()
    serializer_class = quran.serializers.AyahWordSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = AyahWordFilter


class TranslationFilter(filters.FilterSet):
    """Filter translations by surah or ayah number or translation type and language."""
    surah = filters.NumberFilter(field_name='ayah__chapter_id__number')
    ayah = filters.NumberFilter(field_name='ayah__verse_number')
    translation = filters.CharFilter(field_name='resource_name')
    language = filters.CharFilter(field_name='language_name')

    class Meta:
        model = Translation
        fields = ['surah', 'ayah', 'translation', 'language']


class TranslationViewSet(viewsets.ReadOnlyModelViewSet):
    """Read only view set for an ayah's translation."""
    queryset = Translation.objects.all()
    serializer_class = quran.serializers.TranslationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filter_class = TranslationFilter


@api_view(['GET'])
def get_ayah(request, surah, ayah):
    """ Returns the current, next, and previous ayah. Assumes next/previous surah if
    out of bounds.
    :param request: rest API request object.
    :type request: Request
    :param surah: The surah number.
    :type surah: int
    :param ayah: the ayah number.
    :type ayah: int
    :return: A JSON response with the requested text.
    :rtype: Response
    """
    try:
        curr_ayah = model_to_dict(Ayah.objects.get(verse_number=ayah,
                                                   chapter_id__number=surah))
    except Ayah.DoesNotExist:
        return Response({"detail": "Ayah not found"}, status=status.HTTP_404_NOT_FOUND)
    try:
        next_ayah = model_to_dict(Ayah.objects.get(verse_number=ayah+1,
                                                   chapter_id__number=surah))
    except (Ayah.DoesNotExist, AttributeError):
        new_surah = 0 if surah == 114 else surah
        next_ayah = model_to_dict(Ayah.objects.get(verse_number=1,
                                                   chapter_id__number=new_surah+1))
    try:
        prev_ayah = model_to_dict(Ayah.objects.get(verse_number=ayah-1,
                                                   chapter_id__number=surah))
    except (Ayah.DoesNotExist, AttributeError):
        new_surah = 115 if surah == 1 else surah
        prev_ayah = model_to_dict(Ayah.objects.filter(chapter_id__number=new_surah-1).last())
    response = curr_ayah
    words = AyahWord.objects.filter(ayah__verse_number=ayah,
                                    ayah__chapter_id__number=surah)
    translations = Translation.objects.filter(ayah__verse_number=ayah,
                                              ayah__chapter_id__number=surah)
    response['words'] = list(reversed(words.values()))
    response['translations'] = list(translations.values())

    return Response(response)


@api_view(['GET'])
def get_surah(request, surah):
    """Returns the ayahs of specific surah.

    :param request: rest API request object.
    :type request: Request
    :param surah: The surah number
    :type surah: int
    :return: A JSON response with the requested text.
    :rtype: Response
    """
    ayahs = Ayah.objects.filter(chapter_id__number=surah)
    if not ayahs.exists():
        if surah > 114:
            surah = 1
            ayahs = Ayah.objects.filter(chapter_id__number=surah)
        elif surah < 1:
            surah = 114
            ayahs = Ayah.objects.filter(chapter_id__number=surah)
    ayah_list = []
    for ayah in ayahs:
        words = AyahWord.objects.filter(ayah=ayah.id,
                                        ayah__chapter_id__number=surah)
        translations = Translation.objects.filter(ayah__verse_number=ayah.id,
                                                  ayah__chapter_id__number=surah)
        single_response = model_to_dict(ayah)
        single_response['words'] = list(reversed(words.values()))
        single_response['translations'] = list(translations.values())
        ayah_list.append(single_response)
    response = {
        'results': ayah_list,
        'count': len(ayah_list)
    }
    return Response(response)


@api_view(['GET'])
def get_ayah_translit(request):
    """Returns the transliteration text of an ayah.
    Request body should have a JSON with "surah" (int) and "ayah" (int).

    :param request: rest API request object.
    :type request: Request
    :return: A JSON response with the requested text.
    :rtype: Response
    """
    surah = int(request.data['surah'])
    ayah = int(request.data['ayah'])
    line = Translation.objects.get(ayah__surah__number=surah, ayah__number=ayah).text
    # Format as JSON and return response
    result = {"line": line}
    return Response(result)


