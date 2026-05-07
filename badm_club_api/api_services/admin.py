from django.contrib import admin
from django.utils import timezone
from .models import TelegramUser, Trainer, TrainingSession, Booking, Transaction, TrainingSubscription, \
	UserSubscription, Gym


# ---------- Inline-элементы (оставим для удобства) ----------

class BookingInline(admin.TabularInline):
	model = Booking
	extra = 0
	readonly_fields = ('created_at', 'cancelled_at', 'refund_amount')
	fields = ('session', 'status', 'created_at', 'cancelled_at', 'refund_amount')
	show_change_link = True


class TransactionInline(admin.TabularInline):
	model = Transaction
	extra = 1
	fk_name = 'user'
	readonly_fields = ('created_at',)
	fields = ('amount', 'type', 'status', 'booking', 'payment_id', 'admin', 'created_at')
	show_change_link = True


# ---------- Админка TelegramUser ----------

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
	list_display = ('telegram_id', 'full_name', 'phone', 'balance', 'created_at')
	list_filter = ('created_at',)
	search_fields = ('telegram_id', 'full_name', 'phone', 'username')
	ordering = ('-created_at',)
	inlines = [BookingInline, TransactionInline]

	def save_formset(self, request, form, formset, change):
		if formset.model == Transaction:
			instances = formset.save(commit=False)
			for instance in instances:
				if instance.type in [Transaction.TypeChoices.DEPOSIT_CASH,
									 Transaction.TypeChoices.DEPOSIT_ONLINE] and \
						instance.status == Transaction.StatusChoices.SUCCESS:
					user = instance.user
					user.balance += instance.amount
					user.save()
				elif instance.type == Transaction.TypeChoices.REFUND and \
						instance.status == Transaction.StatusChoices.SUCCESS:
					user = instance.user
					user.balance += instance.amount
					user.save()
				instance.save()
			formset.save_m2m()
		else:
			super().save_formset(request, form, formset, change)


# ---------- Админка Trainer ----------

@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
	list_display = ('name', 'is_active', 'telegram_id')
	list_filter = ('is_active',)
	search_fields = ('name',)
	ordering = ('name',)


# ---------- Админка TrainingSession ----------

@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
	list_display = ('id', 'trainer', 'gym', 'start_datetime', 'end_datetime',
					'price', 'max_participants', 'is_group', 'is_cancelled')
	list_filter = ('trainer', 'gym', 'is_group', 'is_cancelled', 'start_datetime')
	search_fields = ('trainer__name', 'location')
	ordering = ('-start_datetime',)
	inlines = [BookingInline]
	actions = ['cancel_session_with_refund']

	@admin.action(description='Отменить тренировку и вернуть 100%% всем участникам')
	def cancel_session_with_refund(self, request, queryset):
		for session in queryset:
			if session.is_cancelled:
				continue
			session.is_cancelled = True
			session.save()
			for booking in session.bookings.filter(status=Booking.StatusChoices.BOOKED):
				booking.status = Booking.StatusChoices.CANCELLED
				booking.cancelled_at = timezone.now()
				booking.refund_amount = session.price
				booking.save()
				Transaction.objects.create(
					user=booking.user,
					amount=session.price,
					type=Transaction.TypeChoices.REFUND,
					status=Transaction.StatusChoices.SUCCESS,
					booking=booking,
					admin=request.user
				)
				booking.user.balance += session.price
				booking.user.save()
		self.message_user(request, "Тренировки отменены, деньги возвращены.")


# ---------- Админка Booking (отдельная таблица) ----------

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'session', 'status', 'created_at', 'cancelled_at', 'refund_amount')
	list_filter = ('status', 'created_at', 'session__trainer')
	search_fields = ('user__full_name', 'user__telegram_id', 'session__trainer__name')
	ordering = ('-created_at',)
	raw_id_fields = ('user', 'session')  # избегаем выпадающих списков, если много записей
	readonly_fields = ('created_at', 'cancelled_at', 'refund_amount')


# ---------- Админка Transaction (отдельная таблица) ----------

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
	list_display = ('id', 'user', 'amount', 'type', 'status', 'payment_id', 'created_at')
	list_filter = ('type', 'status', 'created_at')
	search_fields = ('user__full_name', 'user__telegram_id', 'payment_id')
	ordering = ('-created_at',)
	raw_id_fields = ('user', 'booking', 'admin')
	readonly_fields = ('created_at',)


class UserSubscriptionInline(admin.TabularInline):
	model = UserSubscription
	extra = 0
	readonly_fields = ('purchased_at',)


@admin.register(TrainingSubscription)
class TrainingSubscriptionAdmin(admin.ModelAdmin):
	list_display = ('name', 'count_training', 'price')


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
	list_display = ('user', 'subscription', 'remaining', 'is_active', 'purchased_at')
	list_filter = ('is_active', 'subscription')
	search_fields = ('user__full_name', 'user__telegram_id', 'subscription__name')
	raw_id_fields = ('user',)

@admin.register(Gym)
class GymAdmin(admin.ModelAdmin):
    list_display = ('name', 'address', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'address')