from datetime import datetime, timedelta
from django.utils import timezone
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (TelegramUser,
                     TrainingSubscription,
                     UserSubscription,
                     Gym,
                     Trainer, TrainingSession, Booking)

from .serializers import (VerifySerializer,
                          RegisterSerializer,
                          TelegramUserSerializer,
                          TrainingSubscriptionSerializer,
                          GymSerializer,
                          TrainersSerializer, TrainingSessionSerializer)
import logging
from django.db.models import Count, Q, Prefetch

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


class GetSportsTraining(APIView):
    def get(self, request, type, id):


        if type not in ('gym', 'trainer'):
            return Response({"error": "Неверный тип"}, status=400)

        now = timezone.now()
        local_now = timezone.localtime(now)
        today = local_now.date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_start = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
        week_end = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))

        if type == 'gym':
            base_qs = TrainingSession.objects.filter(gym_id=id, start_datetime__range=(week_start, week_end))
        else:  # trainer
            base_qs = TrainingSession.objects.filter(trainer_id=id, start_datetime__range=(week_start, week_end))

        logger.warning(f"DEBUG: now={now}, today={today}, start_of_week={start_of_week}, end_of_week={end_of_week}")
        logger.warning(f"DEBUG: week_start={week_start}, week_end={week_end}")

        # Оптимизация: подгружаем связанные модели и аннотируем количество активных записей
        qs = base_qs.select_related('trainer', 'gym', 'type') \
                    .prefetch_related('bookings') \
                    .annotate(
                        active_bookings_count=Count(
                            'bookings',
                            filter=Q(bookings__status='booked')
                        )
                    )

        # Передаём аннотированное поле в сериализатор
        serializer = TrainingSessionSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class GetFullBookingTrainers(APIView):
    def get(self, request):
        # Определяем текущую неделю в московском времени
        now = timezone.now()
        local_now = timezone.localtime(now)
        today = local_now.date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        week_start = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
        week_end = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))

        # Базовый QuerySet с фильтром по неделе
        base_qs = TrainingSession.objects.filter(
            start_datetime__range=(week_start, week_end)
        )

        # Оптимизация: подгружаем связанные объекты и аннотируем количество записей
        qs = base_qs.select_related('trainer', 'gym', 'type') \
                    .prefetch_related(
                        Prefetch(
                            'bookings',
                            queryset=Booking.objects.filter(status='booked')
                                                    .select_related('user'),
                            to_attr='active_bookings'
                        )
                    ) \
                    .annotate(
                        active_bookings_count=Count(
                            'bookings',
                            filter=Q(bookings__status='booked')
                        )
                    )

        # Сериализуем
        serializer = TrainingSessionSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)