import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = "admin"
EMAIL = "admin@mirada.local"
PASSWORD = "admin1234"

if not User.objects.filter(username=USERNAME).exists():
    User.objects.create_superuser(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD
    )
    print("✅ Superusuario creado")
else:
    print("ℹ️ Superusuario ya existe")
