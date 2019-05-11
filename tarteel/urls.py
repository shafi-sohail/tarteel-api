# Django
from django.conf import settings
from django.conf.urls import include
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
# REST
from rest_framework import routers
from rest_framework.authtoken import views as authviews
# Tarteel
import audio.views
import evaluation.views
import restapi.views


router = routers.DefaultRouter()
# router.register(r'users', restapi.views.UserViewSet)
# router.register(r'groups', restapi.views.GroupViewSet)

urlpatterns = [
    # Rest API v1
    path('api/', include('restapi.urls')),
    # Top Level API
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/demographics/', restapi.views.DemographicInformationViewList.as_view(),
        name='demographic'),
    url(r'^api/evaluator/', evaluation.views.EvaluationList.as_view(), name="evaluation"),
    url(r'^api/v2/evaluator/', restapi.views.EvaluationList.as_view(), name="v2_evaluation"),
    url(r'^api/v2/submit_evaluation', restapi.views.EvaluationSubmission.as_view(), name="v2_evaluation_submission"),
    url(r'^api/get_evaluations_count/', evaluation.views.get_evaluations_count,
        name="get_evaluations_count"),
    url(r'^get_ayah_translit/', audio.views.get_ayah_translit),
    url(r'^get_total_count/', restapi.views.RecordingsCount.as_view(),
        name='recordingscount'),
    url(r'^api/download-audio/', restapi.views.DownloadAudio.as_view()),
    # Evaluation tools
    url(r'^evaluator/', evaluation.views.evaluator),
    url(r'^evaluation/evaluator/', evaluation.views.evaluator),
    url(r'^evaluation/tajweed/', evaluation.views.tajweed_evaluator),
    url(r'^evaluation/submit_tajweed', evaluation.views.TajweedEvaluationList.as_view(),
        name='tajweed-evaluation'),
    # Django-allauth Login
    url(r'^accounts/', include('allauth.urls')),
    url(r'^api-token-auth/', authviews.obtain_auth_token),
]

urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
