#!/bin/bash

echo "Waiting for PostgreSQL..."
while ! pg_isready -h wingz_db -p 5432 -U wingz_user > /dev/null 2>&1; do
  sleep 1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Starting server..."
exec "$@"
