from collections import defaultdict
from datetime import datetime, timedelta

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
					 Trainer, TrainingSession, Booking)

from .serializers import (VerifySerializer,
						  RegisterSerializer,
						  TelegramUserSerializer,
						  TrainingSubscriptionSerializer,
						  GymSerializer,
						  TrainersSerializer, TrainingSessionSerializer, DailyScheduleSerializer,
						  TrainingDetailSerializer)
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
	"""
    Возвращает список тренировок на текущую неделю, сгруппированный по дням.
    Для каждой тренировки выдаётся расширенная информация + список участников.
    """

	def get(self, request):
		# 1. Вычисляем границы недели в московском времени
		now = timezone.now()
		local_now = timezone.localtime(now)
		today = local_now.date()
		start_of_week = today - timedelta(days=today.weekday())  # понедельник
		end_of_week = start_of_week + timedelta(days=6)  # воскресенье
		week_start = timezone.make_aware(datetime.combine(start_of_week, datetime.min.time()))
		week_end = timezone.make_aware(datetime.combine(end_of_week, datetime.max.time()))

		# 2. Базовый queryset тренировок за неделю
		base_qs = TrainingSession.objects.filter(
			start_datetime__range=(week_start, week_end)
		)

		# 3. Оптимизация: подгрузка связанных данных и аннотация количества записей
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
			user_sub = UserSubscription.objects.filter(
				user=telegram_user,
				is_active=True,
				remaining__gt=0
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

        try:
            amount = int(subscription.price)
        except (TypeError, ValueError):
            return Response({"error": "Цена абонемента некорректна"}, status=400)

        try:
            user = TelegramUser.objects.get(telegram_id=telegram_id)
        except TelegramUser.DoesNotExist:
            return Response({"error": "Пользователь не найден"}, status=404)

        if user.balance < amount:
            return Response(
                {"error": f"Недостаточно средств. Баланс: {user.balance}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        UserSubscription.objects.filter(user=user).delete()

        user_sub = UserSubscription.objects.create(
            user=user,
            subscription=subscription,
            remaining=subscription.count_training,
            is_active=True
        )

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
		except TrainingSession.DoesNotExist:
			return Response({"error": "Тренировка не найдена"}, status=404)

		if Booking.objects.filter(user=user, session=training_session, status='booked').exists():
			return Response(
				{"error": "Вы уже записаны на эту тренировку"},
				status=status.HTTP_400_BAD_REQUEST
			)

		booked_count = Booking.objects.filter(session=training_session, status='booked').count()
		if booked_count >= training_session.max_participants:
			return Response(
				{"error": "Нет свободных мест"},
				status=status.HTTP_400_BAD_REQUEST
			)

		user_sub = UserSubscription.objects.filter(
			user=user,
			is_active=True,
			remaining__gt=0
		).first()

		if not user_sub:
			return Response({"error": "Нет действующего абонемента"}, status=400)

		booking = Booking.objects.create(
			user=user,
			session=training_session,
			status='booked'
		)

		user_sub.remaining -= 1
		user_sub.save()

		if user_sub.remaining == 0:
			user_sub.is_active = False
			user_sub.save()

		return Response({
			"success": True,
			"message": "Вы успешно записаны на тренировку",
			"booking_id": booking.id,
			"remaining_trainings": user_sub.remaining
		}, status=status.HTTP_201_CREATED)
