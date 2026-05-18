from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('auth/verify/', AuthVerifyView.as_view(), name='auth-verify'),
    path('auth/register/', AuthRegisterView.as_view(), name='auth-register'),
    path('user/profile/<int:telegram_id>', GetUserProfileView.as_view(), name='get_profile'),
    path('training-subscriptions/<int:telegram_id>', GetTrainingSubscription.as_view(), name='get_subs'),
    path('gyms/', GetGyms.as_view(), name='get_gyms'),
    path('trainers/', GetTrainers.as_view(), name='get_trainers'),
    path('sport_training/<str:type>/<int:id>/', GetSportsTraining.as_view(), name='sport_training'),
    path('sport_training/full_bookings/', GetFullBookingTrainers.as_view(), name='full_booking_trainers')
]
