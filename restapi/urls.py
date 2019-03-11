from django.urls import path, include
from django.conf.urls import url

from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('recordings', views.model.AnnotatedRecordingViewSet)
router.register('evaluation_set', views.model.EvaluationViewSet)

urlpatterns = [
    # API
    path('', include(router.urls)),
    # Site specific info
    url(r'^api/get_ayah/', views.site.GetAyah.as_view(), name='get_ayah'),
    url(r'^api/index/', views.site.Index.as_view(), name='api_index'),
    url(r'^api/about/', views.site.About.as_view(), name='api_about'),
    url(r'^api/surah/(?:(?P<num>\d+)/)?$', views.site.GetSurah.as_view(), name='get_Surah'),
    url(r'^api/profile/(?P<session_key>[\w-]+)/', views.site.Profile.as_view(), name='profile_api'),
]
