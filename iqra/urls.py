from django.urls import path
from . import views

urlpatterns = [
    path('iqra/search', views.getSearchResult, name='iqra-search'),
    path('iqra/translations', views.getAyahTranslations, name='iqra-translation'),
]
