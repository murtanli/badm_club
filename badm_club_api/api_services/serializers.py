from rest_framework import serializers
from .models import TelegramUser, TrainingSubscription


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
