from django.urls import path

from .views import index, deposit_transfer

urlpatterns = [
    path('', index),
    path('api_v1/deposit_transfer', deposit_transfer)
]