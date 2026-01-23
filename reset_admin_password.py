# reset_admin_password.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username="admin")
user.set_password("admin1234")
user.save()

print("✅ Password reseteado con SECRET_KEY fijo")
