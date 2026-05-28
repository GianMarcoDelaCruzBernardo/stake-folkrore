from django.db import models
from django.conf import settings
from decimal import Decimal
from cloudinary.models import CloudinaryField


class StoreItem(models.Model):
    """Premio disponible en la tienda. El admin lo crea y gestiona."""
    name        = models.CharField(max_length=200, verbose_name="Nombre del premio")
    description = models.TextField(blank=True, verbose_name="Descripcion")
    image       = CloudinaryField("imagen", null=True, blank=True)
    price       = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Precio en soles virtuales",
    )
    stock       = models.PositiveIntegerField(
        default=0,
        verbose_name="Stock disponible (0 = ilimitado)",
        help_text="Pon 0 si es ilimitado (Yape, sorteos, etc.)",
    )
    is_active   = models.BooleanField(default=True, verbose_name="Activo")
    order       = models.PositiveIntegerField(default=1, verbose_name="Orden de aparicion")
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Premio"
        verbose_name_plural = "Premios"
        ordering            = ["order", "price"]

    def __str__(self):
        return f"{self.name} — S/{self.price}"

    def is_available(self):
        """True si tiene stock o es ilimitado."""
        return self.is_active and (self.stock == 0 or self.stock > 0)

    def real_stock_display(self):
        return "Ilimitado" if self.stock == 0 else str(self.stock)


class Redemption(models.Model):
    """Solicitud de canje de un usuario."""

    STATUS_CHOICES = [
        ("pending",   "Pendiente de revision"),
        ("approved",  "Aprobado — entregado"),
        ("rejected",  "Rechazado"),
    ]

    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="redemptions",
    )
    item        = models.ForeignKey(
        StoreItem,
        on_delete=models.PROTECT,
        related_name="redemptions",
        verbose_name="Premio",
    )
    cost_paid   = models.DecimalField(
        max_digits=10, decimal_places=2,
        verbose_name="Soles descontados",
    )
    status      = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name="Estado",
    )

    # Datos de entrega llenados por el usuario
    full_name   = models.CharField(max_length=200, verbose_name="Nombre completo")
    dni         = models.CharField(max_length=20,  verbose_name="DNI")
    phone       = models.CharField(max_length=20,  verbose_name="Celular / Yape")
    city        = models.CharField(max_length=100, verbose_name="Ciudad")
    district    = models.CharField(max_length=100, verbose_name="Distrito")
    address     = models.TextField(verbose_name="Direccion completa")
    notes       = models.TextField(blank=True, verbose_name="Notas adicionales")

    # Control admin
    admin_notes = models.TextField(blank=True, verbose_name="Notas del admin")
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Solicitud de canje"
        verbose_name_plural = "Solicitudes de canje"
        ordering            = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} — {self.item.name} ({self.get_status_display()})"