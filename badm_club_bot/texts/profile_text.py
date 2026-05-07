from decimal import Decimal


def profile_text(*, full_name: str,
                 username: str,
                 telegram_id: int,
                 balance: float,
                 subscription_status: str,
                 completed: int,
                 active_bookings: list[str] | None = None) -> str:
    balance = Decimal(balance)
    lines = [
        "👤 Профиль пользователя",
        "",
        f"Имя: {full_name}",
        f"Username: @{username}",
        f"ID: {telegram_id}",
        f"💳 Баланс: {balance:.2f} руб.",
        "",
        f"🎫 Абонемент: {subscription_status}",
        "",
        "📊 Статистика тренировок:",
        f"• Всего завершено: {completed}",
        "",
        "Активные записи:",
    ]
    if active_bookings:
        lines.extend(f"• {b}" for b in active_bookings)
    else:
        lines.append("У вас нет активных записей.")
    return "\n".join(lines)
