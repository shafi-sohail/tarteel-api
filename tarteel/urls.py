# Django
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
# REST
from rest_framework.authtoken import views as authviews
# Tarteel
import evaluation.views
from restapi.views.site import redirect_to_tarteelio


urlpatterns = [
    path('', redirect_to_tarteelio, name='homepage-redirect'),
    # Rest API v1
    path('v1/', include('restapi.urls')),
    path('v1/', include('evaluation.urls')),
    path('v1/quran/', include('quran.urls')),
    # Iqra
    path('iqra/', include('iqra.urls')),
    # Evaluation tools TODO: Refactor into own interface
    path('api/get_evaluations_count/', evaluation.views.get_evaluations_count,
        name="get_evaluations_count"),
    path('evaluation/tajweed/', evaluation.views.tajweed_evaluator),
    path('evaluation/submit_tajweed', evaluation.views.TajweedEvaluationList.as_view(),
        name='tajweed-evaluation'),
    # Admin Page
    path('admin/', admin.site.urls),
    # Authentication: DRF Auth URLs and user token generation
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', authviews.obtain_auth_token),
    # Django-allauth and rest-auth
    path('', include('profiles.urls')),
    # Pinax Badges
    path('badges/', include("pinax.badges.urls", namespace="pinax_badges")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
