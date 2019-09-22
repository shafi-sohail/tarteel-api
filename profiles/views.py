from django.forms.models import model_to_dict
from django.http import HttpResponseBadRequest

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView, SocialConnectView
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.settings import api_settings

from profiles.models import UserAyah, UserSurah
from quran.models import Ayah


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class UserAyahView(generics.ListCreateAPIView):
    """
    View all ayahs recited by a user and update as needed.

    Requires user authentication.
    """

    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request, *args, **kwargs):
        """Returns a list of recited ayahs for the user."""
        user = request.user
        user_ayahs = UserAyah.objects.filter(user=user).values()
        page = self.paginate_queryset(user_ayahs)
        response = self.get_paginated_response(page)
        return response

    def post(self, request, *args, **kwargs):
        """Updates the count of a user recited ayah by 1."""
        # Parse data
        surah_num = request.data.get('surah', None)
        if surah_num is None:
            return HttpResponseBadRequest("Missing 'surah' field.")

        ayah_num = request.data.get('ayah', None)
        if ayah_num is None:
            return HttpResponseBadRequest("Missing 'ayah' field.")
        try:
            ayah = Ayah.objects.get(chapter_id=surah_num, verse_number=ayah_num)
        except Ayah.DoesNotExist:
            return HttpResponseBadRequest('The surah or ayah provided is out of range.')
        user = request.user

        # Check if the field exists. Otherwise create new record.
        user_ayah, created = UserAyah.objects.get_or_create(user=user, ayah=ayah)
        user_ayah.count += 1
        user_ayah.save()
        result = model_to_dict(user_ayah)
        return Response(result, status=status.HTTP_201_CREATED, content_type="application/json")


class UserSurahView(generics.ListAPIView):
    """
    View all surahs recited by a user.

    Requires user authentication.
    """

    authentication_classes = (authentication.SessionAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request, *args, **kwargs):
        """Return a list of recited surahs for the user."""
        user = request.user
        user_ayahs = UserSurah.objects.filter(user=user).values()
        page = self.paginate_queryset(user_ayahs)
        response = self.get_paginated_response(page)
        return response
