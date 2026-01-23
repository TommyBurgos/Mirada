import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = "admin"
EMAIL = "admin@mirada.local"
PASSWORD = "admin1234"

user, created = User.objects.get_or_create(
    username=USERNAME,
    defaults={
        "email": EMAIL,
        "is_staff": True,
        "is_superuser": True,
    }
)

user.set_password(PASSWORD)
user.is_staff = True
user.is_superuser = True
user.save()

print("✅ Superusuario listo / contraseña reseteada")
