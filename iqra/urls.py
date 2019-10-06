from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.get_search_result, name='iqra-search'),
    path('translations/', views.get_ayah_translations, name='iqra-translation'),
]
