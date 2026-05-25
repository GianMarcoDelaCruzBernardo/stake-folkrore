import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stakefolclor.settings")
django.setup()

from accounts.models import CustomUser

if not CustomUser.objects.filter(email="admin@stakefolclor.com").exists():
    user = CustomUser.objects.create_superuser(
        username="admin",
        email="admin@stakefolclor.com",
        password="Admin2024$"
    )
    print("[OK] Superusuario creado: admin@stakefolclor.com / Admin2024$")
else:
    print("[INFO] El superusuario ya existe.")
