#!/bin/sh

# pwd
# ls -la

python manage.py migrate
python manage.py createcachetable
python manage.py collectstatic

if [ "$DJANGO_SUPERUSER_USERNAME" ]
then
    python manage.py createsuperuser \
        --noinput \
        --username $DJANGO_SUPERUSER_USERNAME \
        --email $DJANGO_SUPERUSER_EMAIL
fi

exec "$@"