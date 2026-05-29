from collections import defaultdict
from datetime import datetime, timedelta

from decimal import Decimal

from django.db import transaction
from django.http import Http404, FileResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import (TelegramUser,
                     TrainingSubscription,
                     UserSubscription,
                     Gym,
                     Trainer, TrainingSession, Booking, Transaction, TelegramAdmin)

from .serializers import (VerifySerializer,
                          RegisterSerializer,
                          TelegramUserSerializer,
                          TrainingSubscriptionSerializer,
                          GymSerializer,
                          TrainersSerializer, TrainingSessionSerializer, DailyScheduleSerializer,
                          TrainingDetailSerializer, UserBookingSerializer)
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

        serializer = TelegramUserSerializer(user)
        data = serializer.data

        active_sub = UserSubscription.objects.filter(
            user=user,
            is_active=True,
            remaining__gt=0
        ).select_related('subscription').first()

        completed_count = Booking.objects.filter(user=user, status='completed').count()
        data['completed'] = completed_count

        if active_sub:
            data['subscription'] = {
                'name': active_sub.subscription.name,
                'remaining': active_sub.remaining,
                'total': active_sub.subscription.count_training,
                'purchased_at': active_sub.purchased_at.strftime("%d.%m.%Y")
            }
        else:
            data['subscription'] = {'message': '0 (не активен)'}

        now = timezone.now()
        user_bookings = Booking.objects.filter(
            user=user,
            status='booked',
            session__start_datetime__gte=now
        ).select_related('session', 'session__type', 'session__gym', 'session__trainer').order_by('session__start_datetime')

        data['user_bookings'] = UserBookingSerializer(user_bookings, many=True).data

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
            "balance": balance,
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

        # Границы текущей недели (пн – вс)
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Преобразуем в datetime с учётом часового пояса
        week_start = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
        week_end = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))

        # Базовый фильтр: тренировки в пределах недели И будущие
        base_qs = TrainingSession.objects.filter(
            start_datetime__range=(week_start, week_end),
            start_datetime__gte=now
        )

        # Уточняем по типу (зал или тренер)
        if type == 'gym':
            base_qs = base_qs.filter(gym_id=id)
        else:  # trainer
            base_qs = base_qs.filter(trainer_id=id)

        logger.debug(f"Week range: {week_start} – {week_end}")
        logger.debug(f"Filtered queryset count: {base_qs.count()}")

        # Оптимизация: подгружаем связанные объекты и аннотируем количество активных записей
        qs = base_qs.select_related('trainer', 'gym', 'type') \
            .prefetch_related('bookings') \
            .annotate(
            active_bookings_count=Count(
                'bookings',
                filter=Q(bookings__status='booked')
            )
        )

        # Сериализуем
        serializer = TrainingSessionSerializer(qs, many=True, context={'request': request})
        return Response(serializer.data)


class GetFullBookingTrainers(APIView):
    """
    Возвращает список тренировок на текущую неделю, сгруппированный по дням.
    Для каждой тренировки выдаётся расширенная информация + список участников.
    """

    def get(self, request):
        now = timezone.now()
        local_now = timezone.localtime(now)
        today = local_now.date()
        start_of_week = today - timedelta(days=today.weekday())  # понедельник
        end_of_week = start_of_week + timedelta(days=6)  # воскресенье
        week_start = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
        week_end = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))

        base_qs = TrainingSession.objects.filter(
            start_datetime__range=(week_start, week_end)
        )

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

        # 4. Группировка по дате (локальной, уже в МСК)
        grouped = defaultdict(list)
        for session in qs:
            # session.start_datetime уже содержит часовой пояс (МСК благодаря настройкам)
            local_date = session.start_datetime.date()
            grouped[local_date].append(session)

        # 5. Преобразуем в список словарей, сортируя по дате
        grouped_list = []
        for date, sessions in sorted(grouped.items()):
            grouped_list.append({
                'date': date.strftime('%d.%m.%y'),  # например, "20.05.26"
                'sessions': sessions
            })

        # 6. Сериализуем и возвращаем
        serializer = DailyScheduleSerializer(grouped_list, many=True)
        return Response(serializer.data)


class TrainerPhotoView(APIView):
    def get(self, request, trainer_id):
        try:
            trainer = Trainer.objects.get(id=trainer_id)
        except Trainer.DoesNotExist:
            raise Http404("Тренер не найден")

        if not trainer.photo:
            raise Http404("Фото не загружено")

        # Открываем файл и отдаём
        return FileResponse(trainer.photo.open(), content_type='image/jpeg')


class GetTrainingSession(APIView):
    def get(self, request, training_id):
        telegram_id = request.query_params.get('telegram_id')
        telegram_user = None
        if telegram_id:
            try:
                telegram_user = TelegramUser.objects.get(telegram_id=telegram_id)
            except TelegramUser.DoesNotExist:
                return Response({"error": "Пользователь не найден"}, status=404)

        # Получаем активный абонемент пользователя (если есть)
        subscription_info = None
        if telegram_user:
            training_session = TrainingSession.objects.get(id=training_id)
            training_type = training_session.type
            allowed_sub_ids = training_type.supported_subscription.values_list('id', flat=True)
            user_sub = UserSubscription.objects.filter(
                user=telegram_user,
                is_active=True,
                remaining__gt=0,
                subscription_id__in=allowed_sub_ids
            ).select_related('subscription').first()
            if user_sub:
                subscription_info = {
                    "subscription_id": user_sub.id,
                    "subscription_name": user_sub.subscription.name,
                    "remaining": user_sub.remaining,
                    "is_active": user_sub.is_active
                }

        try:
            training = TrainingSession.objects.select_related('trainer', 'gym', 'type') \
                .prefetch_related(
                Prefetch(
                    'bookings',
                    queryset=Booking.objects.filter(status='booked').select_related('user'),
                    to_attr='active_bookings'
                )
            ) \
                .annotate(
                bookings_count=Count('bookings', filter=Q(bookings__status='booked'))
            ) \
                .get(id=training_id)
        except TrainingSession.DoesNotExist:
            return Response({"error": "Тренировка не найдена"}, status=404)

        serializer = TrainingDetailSerializer(training, context={
            'request': request,
            'telegram_user': telegram_user,
            'subscription_info': subscription_info  # теперь передаём словарь или None
        })
        return Response(serializer.data)


class PaySubFromBalance(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        subscription_id = request.data.get('subscription_id')

        if not telegram_id or not subscription_id:
            return Response(
                {"error": "Не указаны telegram_id или subscription_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            subscription = TrainingSubscription.objects.get(id=subscription_id)
        except TrainingSubscription.DoesNotExist:
            return Response({"error": "Абонемент не найден"}, status=404)

        amount = subscription.price  # Decimal

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)

        if user.balance < amount:
            return Response(
                {"error": f"Недостаточно средств. Баланс: {user.balance}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Удаляем все старые абонементы пользователя
        UserSubscription.objects.filter(user=user).delete()

        # Создаём новый абонемент
        user_sub = UserSubscription.objects.create(
            user=user,
            subscription=subscription,
            remaining=subscription.count_training,
            is_active=True
        )

        # Создаём транзакцию (без привязки к бронированию)
        Transaction.objects.create(
            user=user,
            amount=amount,
            type=Transaction.TypeChoices.SUBSCRIPTION_PURCHASE,
            status=Transaction.StatusChoices.SUCCESS
            # booking не указываем, так как поле nullable
        )

        # Списываем деньги
        user.balance -= amount
        user.save()

        return Response({
            "success": True,
            "new_balance": float(user.balance),
            "remaining_trainings": user_sub.remaining,
            "message": f"Абонемент «{subscription.name}» приобретён. Осталось тренировок: {user_sub.remaining}"
        }, status=status.HTTP_200_OK)

class CreateBookingSubs(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        training_id = request.data.get('training_id')

        if not telegram_id or not training_id:
            return Response(
                {"error": "Не указаны telegram_id или training_id"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)

        try:
            training_session = TrainingSession.objects.get(id=training_id)
            training_type = training_session.type
            allowed_sub_ids = training_type.supported_subscription.values_list('id', flat=True)
        except TrainingSession.DoesNotExist:
            return Response({"error": "Тренировка не найдена"}, status=404)

        # Проверка, не записан ли уже пользователь
        if Booking.objects.filter(user=user, session=training_session, status='booked').exists():
            return Response(
                {"error": "Вы уже записаны на эту тренировку"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверка свободных мест
        booked_count = Booking.objects.filter(session=training_session, status='booked').count()
        if booked_count >= training_session.max_participants:
            return Response(
                {"error": "Нет свободных мест"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Определяем стоимость тренировки (если есть тип и цена)
        cost = 0
        if training_session.type and training_session.type.price:
            cost = training_session.type.price
        if cost is None:
            cost = Decimal('0')

        # Ищем активный абонемент
        user_sub = UserSubscription.objects.filter(
            user=user,
            is_active=True,
            remaining__gt=0,
            subscription_id__in=allowed_sub_ids
        ).first()

        # Если есть абонемент – списываем с абонемента
        if user_sub:
            booking = Booking.objects.create(
                user=user,
                session=training_session,
                status='booked',
                payment_method='subscription',
                user_subscription=user_sub
            )

            Transaction.objects.create(
                user=user,
                amount=cost,
                type='payment_sub',
                status='success',
                booking=booking,
                created_at=datetime.now()
            )

            user_sub.remaining -= 1
            user_sub.save()
            if user_sub.remaining == 0:
                user_sub.is_active = False
                user_sub.save()
            return Response({
                "success": True,
                "message": "Вы успешно записаны на тренировку (абонемент)",
                "booking_id": booking.id,
                "remaining_trainings": user_sub.remaining
            }, status=status.HTTP_201_CREATED)

        # Если абонемента нет – пытаемся списать с баланса
        if cost == 0:
            return Response(
                {"error": "Стоимость тренировки не определена, невозможно оплатить"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.balance < cost:
            return Response(
                {"error": f"Недостаточно средств. Баланс: {user.balance}, стоимость: {cost}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Списание с баланса
        user.balance -= cost
        user.save()

        booking = Booking.objects.create(
            user=user,
            session=training_session,
            status='booked',
            refund_amount=cost,
            payment_method='balance'
        )

        Transaction.objects.create(
            user=user,
            amount=cost,
            type='payment',
            status='success',
            booking=booking,
            created_at=datetime.now()
        )

        return Response({
            "success": True,
            "message": f"✅ Вы успешно записаны на тренировку (списано {cost} руб. с баланса)",
            "booking_id": booking.id,
            "new_balance": float(user.balance)
        }, status=status.HTTP_201_CREATED)


class CancelBooking(APIView):
    def post(self, request):
        telegram_id = request.data.get('telegram_id')
        training_session_id = request.data.get('training_session_id')

        booking = Booking.objects.filter(
            user__telegram_id=telegram_id,
            session_id=training_session_id,
            status='booked'
        ).select_related('session', 'user', 'user_subscription').first()

        if not booking:
            return Response({"error": "Активная запись не найдена"}, status=404)

        now = timezone.now()
        start_time = booking.session.start_datetime
        hours_until_start = (start_time - now).total_seconds() / 3600

        # Отменяем запись
        booking.status = 'cancelled'
        booking.cancelled_at = now
        booking.save()

        refund_message = ""
        refund_done = False

        if hours_until_start >= 24:
            # Возврат полный
            if booking.payment_method == 'subscription':
                # Вариант A: если в Booking есть связь с UserSubscription
                if booking.user_subscription:
                    user_sub = booking.user_subscription
                    user_sub.remaining += 1
                    user_sub.is_active = True
                    user_sub.save()
                    refund_message = f"Возвращена 1 тренировка в абонемент «{user_sub.subscription.name}». Остаток: {user_sub.remaining}"
                    refund_done = True
                else:
                    # Вариант B: ищем любой активный абонемент пользователя
                    user_sub = UserSubscription.objects.filter(
                        user=booking.user,
                        is_active=True
                    ).first()
                    if user_sub:
                        user_sub.remaining += 1
                        user_sub.save()
                        refund_message = f"Возвращена 1 тренировка в абонемент «{user_sub.subscription.name}». Остаток: {user_sub.remaining}"
                        refund_done = True
                    else:
                        refund_message = "Не найден активный абонемент для возврата тренировки."

            elif booking.payment_method == 'balance':
                cost = booking.session.type.price if booking.session.type else Decimal('0')
                if cost > 0:
                    booking.user.balance += cost
                    booking.user.save()
                    Transaction.objects.create(
                        user=booking.user,
                        amount=cost,
                        type=Transaction.TypeChoices.REFUND,
                        status=Transaction.StatusChoices.SUCCESS,
                        booking=booking,
                    )
                    refund_message = f"Возвращено {cost} руб. на баланс. Новый баланс: {booking.user.balance}"
                    refund_done = True
                else:
                    refund_message = "Стоимость тренировки не определена, возврат не выполнен."
            else:
                refund_message = "Способ оплаты не распознан, возврат не выполнен."
        else:
            refund_message = "❌ Отмена менее чем за 24 часа до начала тренировки — возврат средств не производится."

        return Response({
            "success": True,
            "message": "Запись отменена",
            "refund_message": refund_message,
            "refund_done": refund_done,
            "hours_until_start": round(hours_until_start, 2)
        }, status=200)

class TomorrowBookingsView(APIView):
    def get(self, request):
        tomorrow = timezone.now().date() + timedelta(days=1)
        bookings = Booking.objects.filter(
            session__start_datetime__date=tomorrow,
            status='booked'
        ).select_related('user', 'session__type', 'session__gym')
        data = [
            {
                'telegram_id': b.user.telegram_id,
                'start_time': b.session.start_datetime.strftime('%H:%M'),
                'type_name': b.session.type.name,
                'gym_name': b.session.gym.name,
            }
            for b in bookings
        ]
        return Response(data)

class CheckAdminView(APIView):
    def get(self, request, telegram_id):
        is_admin = TelegramAdmin.objects.filter(telegram_id=telegram_id, is_active=True).exists()
        return Response({"is_admin": is_admin})