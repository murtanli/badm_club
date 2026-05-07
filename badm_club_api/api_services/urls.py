from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('auth/verify/', AuthVerifyView.as_view(), name='auth-verify'),
    path('auth/register/', AuthRegisterView.as_view(), name='auth-register'),
    path('user/profile/<int:telegram_id>', GetUserProfileView.as_view(), name='get_profile'),
    path('training-subscriptions/<int:telegram_id>', GetTrainingSubscription.as_view(), name='get_subs'),
    path('gyms/', GetGyms.as_view(), name='get-gyms'),
    path('trainers/', GetTrainers.as_view(), name='get-trainers'),
]
