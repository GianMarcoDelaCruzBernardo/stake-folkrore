import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crea superusuario desde variables de entorno (seguro para deploy)"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.environ.get("ADMIN_USERNAME")
        email    = os.environ.get("ADMIN_EMAIL")
        password = os.environ.get("ADMIN_PASSWORD")

        if not all([username, email, password]):
            self.stdout.write(self.style.WARNING(
                "Variables ADMIN_USERNAME, ADMIN_EMAIL o ADMIN_PASSWORD no encontradas. Saltando."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"El usuario '{username}' ya existe. No se creo uno nuevo."
            ))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(
            f"Superusuario '{username}' creado correctamente."
        ))
