from django.urls import path
from django.conf.urls import url

from rest_framework import routers
from . import views


router = routers.DefaultRouter()

router.register('recordings', views.model.AnnotatedRecordingViewSet)
router.register('evaluation_set', views.model.EvaluationViewSet)

urlpatterns = [
    # Site specific info
    path('get_ayah/', views.site.GetAyah.as_view(), name='get_ayah'),
    url(r'^index/', views.site.Index.as_view(), name='api_index'),
    url(r'^about/', views.site.About.as_view(), name='api_about'),
    url(r'^surah/(?P<surah_num>\d+)', views.site.GetSurah.as_view(), name='get_surah'),
    url(r'^profile/(?P<session_key>[\w-]+)/', views.site.Profile.as_view(), name='profile_api'),
]

urlpatterns += router.urls
