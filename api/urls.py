from django.urls import path
from . import views

urlpatterns = [
    path('get-treatment/', views.get_treatment, name='get-treatment'),
    path('icd-codes/', views.get_icd_codes, name='icd-codes'),
]
