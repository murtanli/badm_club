FROM python:3.11

# Устанавливаем рабочую директорию
WORKDIR /usr/src/badm_club_bot

# Копируем зависимости и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь код
COPY . .

CMD ["python", "./bot.py"]

