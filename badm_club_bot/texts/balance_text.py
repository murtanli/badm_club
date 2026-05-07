from decimal import Decimal


def balance_text(balance: float, subscription_status: dict | None = None) -> str:
    balance = Decimal(balance)
    lines = [f"💳 Ваш баланс: {balance:.2f} руб."]

    if not subscription_status:
        return "\n".join(lines)

    # Если пришёл объект с сообщением (нет активного абонемента)
    if 'message' in subscription_status:
        lines.append(f"🎫 Абонемент: {subscription_status['message']}")
    else:
        # Есть активный абонемент: name, remaining, total, purchased_at
        name = subscription_status.get('name', '')
        remaining = subscription_status.get('remaining', 0)
        total = subscription_status.get('total', 0)
        purchased = subscription_status.get('purchased_at', '')
        lines.append(
            f"🎫 Абонемент: «{name}»: \n"
            f"осталось {remaining} из {total} тренировок (куплен {purchased})"
        )

    return "\n".join(lines)