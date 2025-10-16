#!/bin/bash

while ! nc -z $DB_HOST $DB_PORT; do
  echo "Waiting for Postgres at $DB_HOST:$DB_PORT..."
  sleep 2
done

# Катим базовые джанговые миграции
python my_site/manage.py migrate

# Катим миграхи нашего приложения
python my_site/manage.py migrate app_next

exec "$@"
