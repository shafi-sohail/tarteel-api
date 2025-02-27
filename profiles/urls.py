from django.urls import path, re_path, include
from .views import FacebookConnect, FacebookLogin
from profiles.views import UserAyahView, UserSurahView, UserSessionView

urlpatterns = [
    path('profile/recited_ayahs/', UserAyahView.as_view(), name='user_ayah'),
    path('profile/recited_surahs/', UserSurahView.as_view(), name='user_surah'),
    path('profile/session/', UserSessionView.as_view(), name='user_session'),
    path('accounts/', include('allauth.urls')),
    path('rest-auth/', include('rest_auth.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    re_path(r'^rest-auth/facebook/$', FacebookLogin.as_view(), name='fb_login'),
    re_path(r'^rest-auth/facebook/connect/$', FacebookConnect.as_view(), name='fb_connect'),
]
