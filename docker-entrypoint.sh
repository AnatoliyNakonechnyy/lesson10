#!/bin/bash
set -e
echo "Очікування запуску PostgreSQL..."
python -c "
import socket
import time
import os
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        s.connect(('${DB_HOST}', int('${DB_PORT}')))
        s.close()
        break
    except socket.error:
        time.sleep(0.5)
"
echo "PostgreSQL запущено!"
echo "Застосування міграцій бази даних..."
python manage.py migrate --noinput
echo "Збір статичних файлів..."
python manage.py collectstatic --noinput
exec "$@"
