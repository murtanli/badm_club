from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (TelegramUser,
                     TrainingSubscription,
                     UserSubscription,
                     Gym,
                     Trainer)

from .serializers import (VerifySerializer,
                          RegisterSerializer,
                          TelegramUserSerializer,
                          TrainingSubscriptionSerializer,
                          GymSerializer,
                          TrainersSerializer)
import logging

logger = logging.getLogger("api")


class AuthVerifyView(APIView):
    """Проверка, зарегистрирован ли пользователь в системе."""
    def post(self, request):
        serializer = VerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        telegram_id = serializer.validated_data['telegram_id']
        user = TelegramUser.objects.filter(telegram_id=telegram_id).first()
        if user:
            return Response({
                'registered': True,
                'user': TelegramUserSerializer(user).data
            })
        return Response({
            'registered': False
        })


class AuthRegisterView(APIView):
    """Регистрация нового пользователя (бота)."""
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        telegram_id = serializer.validated_data['telegram_id']

        # Проверяем, вдруг кто-то уже зарегистрирован с таким telegram_id
        if TelegramUser.objects.filter(telegram_id=telegram_id).exists():
            return Response(
                {'error': 'Пользователь с таким Telegram ID уже зарегистрирован'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = serializer.save()
        return Response(
            TelegramUserSerializer(user).data,
            status=status.HTTP_201_CREATED
        )


class GetUserProfileView(APIView):
    def get(self, request, telegram_id):
        if not telegram_id:
            return Response({"error": "telegram_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            logger.warning(f"Пользователь с telegram_id={telegram_id} не найден")
            return Response({"error": "profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Основные данные профиля
        serializer = TelegramUserSerializer(user)
        data = serializer.data

        # Активный абонемент (если есть)
        active_sub = UserSubscription.objects.filter(
            user=user,
            is_active=True,
            remaining__gt=0
        ).select_related('subscription').first()

        if active_sub:
            data['subscription'] = {
                'name': active_sub.subscription.name,
                'remaining': active_sub.remaining,
                'total': active_sub.subscription.count_training,
                'purchased_at': active_sub.purchased_at.strftime("%d.%m.%Y")
            }
        else:
            data['subscription'] = {'message': '0 тренировок'}

        return Response(data, status=status.HTTP_200_OK)


class GetTrainingSubscription(APIView):
    def get(self, request, telegram_id):

        if not telegram_id:
            return Response({"error": "telegram_id обязателен"}, status=status.HTTP_400_BAD_REQUEST)

        # Ищем пользователя
        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            logger.warning(f"Пользователь с telegram_id={telegram_id} не найден")
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        # Все абонементы, доступные для покупки
        all_subs = TrainingSubscription.objects.all()
        subs_data = TrainingSubscriptionSerializer(all_subs, many=True).data

        balance = user.balance

        # Активный абонемент пользователя (первый с remaining > 0)
        active_sub = UserSubscription.objects.filter(
            user=user,
            is_active=True,
            remaining__gt=0
        ).select_related('subscription').first()

        if active_sub:
            user_sub_info = {
                "name": active_sub.subscription.name,
                "remaining": active_sub.remaining,
                "total": active_sub.subscription.count_training,
                "purchased_at": active_sub.purchased_at.strftime("%d.%m.%Y")
            }
        else:
            user_sub_info = {"message": "0 тренировок"}

        return Response({
            "balance":balance,
            "available_subscriptions": subs_data,
            "user_subscription": user_sub_info
        }, status=status.HTTP_200_OK)

class GetGyms(APIView):
    def get(self, request):
        gyms = Gym.objects.all()
        serializer = GymSerializer(instance=gyms, many=True)
        return Response({"gyms": serializer.data}, status=status.HTTP_200_OK)

class GetTrainers(APIView):
    def get(self, request):
        trainers = Trainer.objects.all()
        serializer = TrainersSerializer(instance=trainers, many=True)
        return Response({"trainers": serializer.data}, status=status.HTTP_200_OK)

