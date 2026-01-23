import os
import django
import sys

print("🚀 Iniciando create_superuser.py", flush=True)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("🔍 Modelo de usuario:", User, flush=True)
print("🔍 DB ENGINE:", os.environ.get("DATABASE_URL"), flush=True)

USERNAME = "admin"
EMAIL = "admin@mirada.local"
PASSWORD = "admin1234"

qs = User.objects.filter(username=USERNAME)
print("🔎 Usuarios encontrados con username=admin:", qs.count(), flush=True)

user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={
        "email": EMAIL,
        "is_staff": True,
        "is_superuser": True,
    }
)

print("🆕 Usuario creado?", created, flush=True)

user.set_password(PASSWORD)
user.is_staff = True
user.is_superuser = True
user.save()

print("✅ Usuario guardado correctamente", flush=True)
