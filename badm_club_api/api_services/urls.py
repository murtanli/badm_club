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
    path('sport_training_list/<str:type>/<int:id>/', GetSportsTraining.as_view(), name='sport_trainings'),
    path('sport_training/full_bookings/', GetFullBookingTrainers.as_view(), name='full_booking_trainers'),
    path('sport_training/trainer-photo/<int:trainer_id>/', TrainerPhotoView.as_view(), name='trainer-photo'),
    path('training/<int:training_id>/', GetTrainingSession.as_view(), name='get-training-session'),
    path('balance/pay_sub_from_balance/', PaySubFromBalance.as_view(), name='pay-from-balance'),
    path('booking/create_booking_from_subscription/', CreateBookingSubs.as_view(), name='create-booking-from-subscription'),
    path('booking/cancel', CancelBooking.as_view(), name='cancel-booking'),
    path('user/notification/tomorrow-training/', TomorrowBookingsView.as_view(), name='notification-training'),
    path('admin/check/<int:telegram_id>/', CheckAdminView.as_view(), name='check-admin'),
]
