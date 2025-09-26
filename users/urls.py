from django.urls import path, include
from . import views

urlpatterns = [
    path('registration/', views.registration_api_view),
    path('authorization/', views.authorization_api_view),
    path('confirm/', views.users_confirm_api_view),
]