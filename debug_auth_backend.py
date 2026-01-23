import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")
django.setup()

from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

print("🔐 AUTHENTICATION_BACKENDS activos:")
for b in settings.AUTHENTICATION_BACKENDS:
    print(" -", b)

User = get_user_model()
user = User.objects.get(username="admin")

print("🧪 Probando authenticate()...")
res = authenticate(username="admin", password="admin1234")
print("Resultado:", res)
