release: python manage.py makemigrations && python manage.py migrate
web: gunicorn authors.wsgi --log-file -
