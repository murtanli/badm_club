from django.urls import reverse
from django.utils import timezone
from rest_framework import serializers
from .models import TelegramUser, TrainingSubscription, Gym, Trainer, TrainingSession


class TelegramUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'username', 'full_name', 'phone', 'balance', 'created_at']
        read_only_fields = ['balance', 'created_at']


class VerifySerializer(serializers.Serializer):
    telegram_id = serializers.IntegerField()


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'full_name', 'phone', 'username']
        extra_kwargs = {
            'telegram_id': {'required': True},
            'full_name': {'required': True},
            'phone': {'required': True},
            'username': {'required': False}
        }


class TrainingSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSubscription
        fields = ['id', 'name', 'count_training', 'description', 'price']


class GymSerializer(serializers.ModelSerializer):
    class Meta:
        model = Gym
        fields = ['id', 'name', 'address', 'description', 'is_active']


class TrainersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trainer
        fields = ['id', 'name', 'description', 'telegram_id', 'is_active']


class TrainingSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    gym_name = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    start_datetime = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    updated_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')

    # НОВЫЕ ПОЛЯ
    weekday = serializers.SerializerMethodField()
    bookings_count = serializers.SerializerMethodField()
    occupancy = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = [
            'id', 'trainer', 'trainer_name',
            'gym', 'gym_name',
            'type', 'type_name',
            'start_datetime', 'weekday',
            'max_participants', 'bookings_count', 'occupancy',
            'is_group', 'is_cancelled',
            'created_at', 'updated_at'
        ]

    def get_trainer_name(self, obj):
        return obj.trainer.name if obj.trainer else None

    def get_gym_name(self, obj):
        return [obj.gym.name, obj.gym.address] if obj.gym else None

    def get_type_name(self, obj):
        return obj.type.name if obj.type else None

    def get_weekday(self, obj):
        # Дни недели на русском
        weekdays_ru = {
            0: 'Понедельник', 1: 'Вторник', 2: 'Среда',
            3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'
        }
        # weekday() возвращает 0-6 (пн-вс)
        return weekdays_ru.get(obj.start_datetime.weekday())

    def get_bookings_count(self, obj):
        # Считаем только активные записи (не отменённые)
        # Если вы хотите учитывать только статус BOOKED, делаем фильтр
        return obj.bookings.filter(status='booked').count()

    def get_occupancy(self, obj):
        # Заполненность в процентах (целое число)
        if obj.max_participants <= 0:
            return 0
        booked = self.get_bookings_count(obj)
        return int((booked / obj.max_participants) * 100)

# ----- Краткий сериализатор участника -----
class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'full_name', 'username']

# ----- Основной сериализатор тренировки -----
class TrainingSessionSerializer(serializers.ModelSerializer):
    trainer_name = serializers.SerializerMethodField()
    gym_name = serializers.SerializerMethodField()
    type_name = serializers.SerializerMethodField()
    start_datetime = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    created_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    updated_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    weekday = serializers.SerializerMethodField()
    bookings_count = serializers.SerializerMethodField()
    occupancy = serializers.SerializerMethodField()
    participants = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    gym_address = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = [
            'id',
            'trainer', 'trainer_name',
            'gym', 'gym_name', 'gym_address',
            'type', 'type_name',
            'start_datetime', 'weekday',
            'time',
            'max_participants', 'bookings_count', 'occupancy',
            'is_group', 'is_cancelled',
            'created_at', 'updated_at',
            'participants'
        ]

    def get_time(self, obj):
        local_dt = timezone.localtime(obj.start_datetime)
        return local_dt.strftime('%H:%M')

    def get_trainer_name(self, obj):
        return obj.trainer.name if obj.trainer else None

    def get_gym_name(self, obj):
        return obj.gym.name if obj.gym else None

    def get_gym_address(self, obj):
        return obj.gym.address if obj.gym else None

    def get_type_name(self, obj):
        return obj.type.name if obj.type else None

    def get_weekday(self, obj):
        weekdays_ru = {
            0: 'Понедельник', 1: 'Вторник', 2: 'Среда',
            3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'
        }
        return weekdays_ru.get(obj.start_datetime.weekday())

    def get_bookings_count(self, obj):
        if hasattr(obj, 'active_bookings_count'):
            return obj.active_bookings_count
        return obj.bookings.filter(status='booked').count()

    def get_occupancy(self, obj):
        if obj.max_participants <= 0:
            return 0
        booked = self.get_bookings_count(obj)
        return int((booked / obj.max_participants) * 100)

    def get_participants(self, obj):
        # Используем предзагруженные активные бронирования (active_bookings)
        bookings = getattr(obj, 'active_bookings', None)
        if bookings is None:
            bookings = obj.bookings.filter(status='booked').select_related('user')
        return [
            {
                'full_name': b.user.full_name,
                'telegram_id': b.user.telegram_id,
                'username': b.user.username,
                'booked_at': b.created_at.strftime('%d.%m.%Y %H:%M') if b.created_at else None
            }
            for b in bookings
        ]

# ----- Сериализатор для группировки по дням -----
class DailyScheduleSerializer(serializers.Serializer):
    date = serializers.CharField()          # дата в формате "DD.MM.YY"
    sessions = TrainingSessionSerializer(many=True)   # список тренировок в этот день


class TrainingDetailSerializer(serializers.ModelSerializer):
    # --- Кастомные поля из связанных моделей ---
    trainer_name = serializers.CharField(source='trainer.name', read_only=True)
    trainer_photo = serializers.SerializerMethodField()
    gym_name = serializers.CharField(source='gym.name', read_only=True)
    gym_address = serializers.CharField(source='gym.address', read_only=True)
    type_name = serializers.CharField(source='type.name', read_only=True)
    type_description = serializers.CharField(source='type.description', read_only=True, default='')
    cost = serializers.DecimalField(source='type.price', max_digits=10, decimal_places=2, read_only=True)

    # --- Время и день недели ---
    start_datetime = serializers.DateTimeField(format='%d.%m.%Y %H:%M')
    weekday = serializers.SerializerMethodField()

    # --- Участники ---
    bookings_count = serializers.IntegerField(read_only=True)
    participants = serializers.SerializerMethodField()

    # --- Баланс пользователя (из контекста) ---
    user_balance = serializers.SerializerMethodField()

    class Meta:
        model = TrainingSession
        fields = [
            'id',
            'trainer_name', 'trainer_photo', 'trainer',
            'gym_name', 'gym_address',
            'type_name', 'type_description', 'cost',
            'start_datetime', 'weekday',
            'max_participants', 'bookings_count', 'participants',
            'is_group', 'is_cancelled',
            'user_balance',
        ]



    def get_trainer_photo(self, obj):
        """Возвращает URL для получения фото тренера через отдельный эндпоинт"""
        if obj.trainer and obj.trainer.photo:
            return reverse('trainer-photo', kwargs={'trainer_id': obj.trainer.id})
        return None

    def get_weekday(self, obj):
        weekdays_ru = {
            0: 'Понедельник', 1: 'Вторник', 2: 'Среда',
            3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'
        }
        return weekdays_ru.get(obj.start_datetime.weekday())

    def get_participants(self, obj):
        """Возвращает список активных участников (статус 'booked')"""
        # Используем предзагруженные через Prefetch бронирования (active_bookings)
        bookings = getattr(obj, 'active_bookings', None)
        if bookings is None:
            bookings = obj.bookings.filter(status='booked').select_related('user')
        return [
            {
                'full_name': b.user.full_name,
                'telegram_id': b.user.telegram_id,
                'username': b.user.username or '',
            }
            for b in bookings
        ]

    def get_user_balance(self, obj):
        """Баланс пользователя из контекста сериализатора"""
        user = self.context.get('telegram_user')
        if user and hasattr(user, 'balance'):
            return float(user.balance)
        return 0.0