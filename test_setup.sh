# Test PostgreSQL connection
python manage.py dbshell

# Test Redis connection
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value', 30)
>>> cache.get('test')
'value'

# Test the application
python manage.py runserver
# Visit: http://localhost:8000/properties/
# Visit: http://localhost:8000/admin/
