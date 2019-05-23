from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.getSearchResult, name='iqra-search'),
    path('translations/', views.getAyahTranslations, name='iqra-translation'),
]
