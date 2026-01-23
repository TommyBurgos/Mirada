import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

User = get_user_model()

print("🔎 Total usuarios:", User.objects.count())

try:
    user = User.objects.get(username="admin")
    print("👤 Usuario encontrado")
    print("is_staff:", user.is_staff)
    print("is_superuser:", user.is_superuser)
    print("is_active:", user.is_active)

    user_check = authenticate(username="admin", password="admin1234")
    print("🔐 authenticate() devuelve:", user_check)

except User.DoesNotExist:
    print("❌ Usuario admin NO existe")
