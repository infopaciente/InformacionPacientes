#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# --- INICIO DEL CÓDIGO NUEVO ---
# Crea un superusuario automáticamente si las variables de entorno existen
# Esto evita que intente crearlo en cada despliegue y falle

echo "Creando superusuario (si no existe)..."
python manage.py shell << END
import os
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username=os.environ.get('DJANGO_SUPERUSER_USERNAME')).exists():
    User.objects.create_superuser(
        username=os.environ.get('DJANGO_SUPERUSER_USERNAME'),
        email=os.environ.get('DJANGO_SUPERUSER_EMAIL'),
        password=os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    )
    print('¡Superusuario creado!')
else:
    print('El superusuario ya existe.')
END
# --- FIN DEL CÓDIGO NUEVO ---