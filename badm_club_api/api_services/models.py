from django.db import models
from django.conf import settings


class TelegramUser(models.Model):
    telegram_id = models.BigIntegerField(unique=True, verbose_name="Telegram ID")
    username = models.CharField(max_length=255, blank=True, null=True, verbose_name="@username")
    full_name = models.CharField(max_length=255, verbose_name="Фамилия Имя")
    phone = models.CharField(max_length=20, verbose_name="Номер телефона")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Баланс")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.full_name} ({self.telegram_id})"

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Trainer(models.Model):
    name = models.CharField(max_length=100, verbose_name="Имя тренера")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    telegram_id = models.BigIntegerField(blank=True, null=True, verbose_name="Telegram ID тренера")
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тренер"
        verbose_name_plural = "Тренеры"


class TrainingSession(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE, related_name='sessions')
    start_datetime = models.DateTimeField(verbose_name="Начало")
    end_datetime = models.DateTimeField(verbose_name="Окончание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Стоимость")
    max_participants = models.PositiveSmallIntegerField(verbose_name="Максимум участников")
    is_group = models.BooleanField(default=True, verbose_name="Групповая тренировка")
    location = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес/Корт")
    is_cancelled = models.BooleanField(default=False, verbose_name="Отменена администратором")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.trainer.name} - {self.start_datetime:%d.%m.%Y %H:%M}"

    class Meta:
        verbose_name = "Тренировка"
        verbose_name_plural = "Тренировки"


class Booking(models.Model):
    class StatusChoices(models.TextChoices):
        BOOKED = 'booked', 'Забронировано'
        CANCELLED = 'cancelled', 'Отменено'

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='bookings')
    session = models.ForeignKey(TrainingSession, on_delete=models.CASCADE, related_name='bookings')
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.BOOKED)
    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True,
                                         verbose_name="Сумма возврата")

    def __str__(self):
        return f"{self.user.full_name} -> {self.session}"

    class Meta:
        verbose_name = "Запись"
        verbose_name_plural = "Записи"


class Transaction(models.Model):
    class TypeChoices(models.TextChoices):
        DEPOSIT_ONLINE = 'deposit_online', 'Пополнение онлайн'
        DEPOSIT_CASH = 'deposit_cash', 'Пополнение наличными'
        PAYMENT = 'payment', 'Оплата тренировки'
        REFUND = 'refund', 'Возврат'
        SUBSCRIPTION_PURCHASE = 'subscription_purchase', 'Покупка абонемента'

    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Ожидает'
        SUCCESS = 'success', 'Успешно'
        FAILED = 'failed', 'Ошибка'

    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(max_length=30, choices=TypeChoices.choices)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, blank=True, null=True,
                                related_name='transactions', verbose_name="Связанная запись")
    payment_id = models.CharField(max_length=255, blank=True, null=True, verbose_name="ID платежа ЮKassa")
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, blank=True, null=True,
                              verbose_name="Администратор (наличные)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type} {self.amount}₽ ({self.user.full_name})"

    class Meta:
        verbose_name = "Транзакция"
        verbose_name_plural = "Транзакции"


class TrainingSubscription(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    count_training = models.PositiveIntegerField(verbose_name="Количество тренировок")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Цена")

    def __str__(self):
        return f"{self.name} ({self.count_training} занятий)"

    class Meta:
        verbose_name = "Абонемент"
        verbose_name_plural = "Абонементы"


class UserSubscription(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='subscriptions')
    subscription = models.ForeignKey(TrainingSubscription, on_delete=models.CASCADE, related_name='user_subscriptions')
    remaining = models.PositiveIntegerField(verbose_name="Осталось тренировок")
    purchased_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активен")

    def __str__(self):
        return f"{self.user.full_name} — {self.subscription.name} (осталось {self.remaining})"

    class Meta:
        verbose_name = "Купленный абонемент"
        verbose_name_plural = "Купленные абонементы"