import datetime
from typing import Any, Dict, Tuple

from django.forms.models import model_to_dict
from django.http import HttpResponseBadRequest

from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from rest_auth.registration.views import SocialLoginView, SocialConnectView
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import status
from rest_framework import generics
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings

from profiles.models import UserAyah, UserSurah, UserSession, UserProfile
from profiles.serializers import UserSessionSerializer
from quran.models import Ayah


def _new_user_ayah(user: UserProfile,  ayah: Ayah, save: bool = True, get_create: bool = False
                   ) -> Tuple[Dict[str, Any],  bool]:
    user_ayah, created = UserAyah.objects.get_or_create(user=user, ayah=ayah)
    user_ayah.count += 1
    if save:
        user_ayah.save()
    if get_create:
        return user_ayah, created
    else:
        return user_ayah


def _get_user_session_data(request: Request) -> Dict[str, Any]:
    data_to_get = ['start_surah', 'start_ayah', 'end_surah', 'end_ayah']
    data = {}
    # DataDataDataDataDataDataDataDataDataDataDataDataDataDataDataDataDataDataDataData BATMAN!!
    for post_data in data_to_get:
        new_data = request.data.get(post_data, None)
        if new_data is None:
            raise ValueError("Missing '{}' field.".format(post_data))
        else:
            data[post_data] = new_data
    # Create the session duration field (Type: datetime.timedelta())
    req_session_time = request.data.get('session_time', None)
    if req_session_time is None:
        raise ValueError('Missing \'session_time\' field.')
    data['session_time'] = datetime.timedelta(seconds=req_session_time)
    return data


class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter


class FacebookConnect(SocialConnectView):
    adapter_class = FacebookOAuth2Adapter


class UserAyahView(generics.ListCreateAPIView):
    """
    View all ayahs recited by a user and update as needed.

    Requires user authentication.
    """

    authentication_classes = (authentication.TokenAuthentication,)
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

        # Check if the field exists. Otherwise create new record.
        user = request.user
        user_ayah = _new_user_ayah(user=user, ayah=ayah)
        result = model_to_dict(user_ayah)
        return Response(result, status=status.HTTP_201_CREATED, content_type="application/json")


class UserSurahView(generics.ListAPIView):
    """
    View all surahs recited by a user.

    Requires user authentication.
    """

    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request, *args, **kwargs):
        """Return a list of recited surahs for the user."""
        user = request.user
        user_ayahs = UserSurah.objects.filter(user=user).values()
        page = self.paginate_queryset(user_ayahs)
        response = self.get_paginated_response(page)
        return response


class UserSessionView(generics.ListCreateAPIView):
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = api_settings.DEFAULT_PAGINATION_CLASS

    def get(self, request,  *args, **kwargs):
        """Returns a list of all the user's recorded sessions."""
        user = request.user
        user_ayahs = UserSession.objects.filter(user=user).values()
        page = self.paginate_queryset(user_ayahs)
        response = self.get_paginated_response(page)
        return response

    def post(self, request, *args, **kwargs):
        """Creates a new session entry for the user."""
        # Parse the request data, returning a bad request accordingly.
        try:
            data = _get_user_session_data(request=request)
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

        # If we only have one surah, get all the ayah's in that surah
        if data.get('start_surah') == data.get('end_surah'):
            ayahs = Ayah.objects.filter(
                chapter_id__number=data.get('start_surah'),
                verse_number__range=(data.get('start_ayah'), data.get('end_ayah')))
        else:
            # Starting surah ayahs
            ayahs = Ayah.objects.filter(
                chapter_id__number=data.get('start_surah'),
                verse_number__gte=data.get('start_ayah'))
            # Middle range ayahs
            for s in range(data.get('start_surah')+1, data.get('end_surah')):
                ayahs.union(Ayah.objects.filter(chapter_id__number=s))
            # Last ayah
            ayahs.union(Ayah.objects.filter(chapter_id__number=data.get('end_surah'),
                                            verse_number__lte=data.get('end_ayah')))

        # Construct the new session instance
        user = request.user
        user_ayahs = [_new_user_ayah(user=user, ayah=a) for a in ayahs]
        user_surahs = UserSurah.objects.filter(
            user=user,
            surah__number__range=(data['start_surah'], data['end_surah']))
        session_time = data.get('session_time')
        new_user_session = UserSession(user=user, session_time=session_time)
        new_user_session.save()
        new_user_session.ayahs.add(*user_ayahs)
        new_user_session.surahs.add(*user_surahs)
        new_user_session.save()

        serialized_result = UserSessionSerializer(new_user_session)
        return Response(serialized_result.data, status=status.HTTP_201_CREATED)
