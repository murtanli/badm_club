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

from rest_framework import serializers
from .models import TrainingSession, Booking, TelegramUser

# Сериализатор для краткой информации об участнике
class UserBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = ['telegram_id', 'full_name', 'username']  # при необходимости добавьте phone и др.

# Сериализатор для бронирования (можно не создавать отдельный, а использовать метод)
class BookingParticipantSerializer(serializers.Serializer):
    full_name = serializers.CharField(source='user.full_name')
    telegram_id = serializers.IntegerField(source='user.telegram_id')
    username = serializers.CharField(source='user.username')
    booked_at = serializers.DateTimeField(format='%d.%m.%Y %H:%M', source='created_at')
    # можно добавить status, если нужно

# Основной сериализатор тренировки
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

    class Meta:
        model = TrainingSession
        fields = [
            'id', 'trainer', 'trainer_name', 'gym', 'gym_name', 'type', 'type_name',
            'start_datetime', 'weekday', 'max_participants', 'bookings_count', 'occupancy',
            'is_group', 'is_cancelled', 'created_at', 'updated_at',
            'participants'
        ]

    def get_trainer_name(self, obj):
        return obj.trainer.name if obj.trainer else None

    def get_gym_name(self, obj):
        return obj.gym.name if obj.gym else None

    def get_type_name(self, obj):
        return obj.type.name if obj.type else None

    def get_weekday(self, obj):
        weekdays_ru = {
            0: 'Понедельник', 1: 'Вторник', 2: 'Среда',
            3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'
        }
        return weekdays_ru.get(obj.start_datetime.weekday())

    def get_bookings_count(self, obj):
        # Используем аннотацию из view, если есть, иначе считаем
        if hasattr(obj, 'active_bookings_count'):
            return obj.active_bookings_count
        return obj.bookings.filter(status='booked').count()

    def get_occupancy(self, obj):
        if obj.max_participants <= 0:
            return 0
        booked = self.get_bookings_count(obj)
        return int((booked / obj.max_participants) * 100)

    def get_participants(self, obj):
        # Используем предзагруженные через prefetch_related активные бронирования
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