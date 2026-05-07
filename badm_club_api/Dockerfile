FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/badm_club_api

COPY ./requirements.txt /usr/src/requirements.txt
RUN pip install --no-cache-dir -r /usr/src/requirements.txt


COPY . /usr/src/badm_club_api

EXPOSE 8100

RUN python manage.py collectstatic --noinput
# CMD запускаем Gunicorn вместо runserver
CMD ["gunicorn", "badm_club_api.wsgi:application", "--bind", "0.0.0.0:8100", "--workers", "3"]
