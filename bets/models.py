"""
bets/models.py
==============
Modelos de apuestas. Sin logica de negocio (esta en services.py).
"""
from django.db import models
from django.conf import settings
from decimal import Decimal


class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wallet"
    )
    balance   = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("50.00"))
    total_won  = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total_lost = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        verbose_name = "Billetera"
        verbose_name_plural = "Billeteras"

    def __str__(self):
        return f"{self.user.username} — S/{self.balance}"


class BetOption(models.Model):
    TYPE_CHOICES = [
        ("block_qualifier", "Clasificado de Bloque"),
        ("champion", "Campeon de Final"),
    ]
    contest    = models.ForeignKey("contests.Contest", on_delete=models.CASCADE, related_name="bet_options")
    bet_type   = models.CharField(max_length=30, choices=TYPE_CHOICES)
    block      = models.ForeignKey("contests.Block", on_delete=models.SET_NULL, null=True, blank=True)
    group_name = models.CharField(max_length=200)
    group_logo = models.ImageField(upload_to="bet_logos/", null=True, blank=True)
    odds       = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.53"))
    is_active  = models.BooleanField(default=False)   # admin activa manualmente
    is_resolved = models.BooleanField(default=False)
    won        = models.BooleanField(null=True, blank=True)

    class Meta:
        verbose_name = "Opcion de Apuesta"
        verbose_name_plural = "Opciones de Apuesta"
        ordering  = ["bet_type", "block__order", "odds"]
        indexes   = [
            models.Index(fields=["contest", "bet_type", "is_active", "is_resolved"]),
        ]

    def __str__(self):
        return f"{self.contest} | {self.get_bet_type_display()} | {self.group_name} @{self.odds}"


class Bet(models.Model):
    STATUS = [
        ("pending", "Pendiente"),
        ("won",     "Ganada"),
        ("lost",    "Perdida"),
    ]
    user          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bets")
    option        = models.ForeignKey(BetOption, on_delete=models.CASCADE, related_name="bets")
    amount        = models.DecimalField(max_digits=8, decimal_places=2)
    odds_at_bet   = models.DecimalField(max_digits=5, decimal_places=2)
    potential_win = models.DecimalField(max_digits=10, decimal_places=2)
    status        = models.CharField(max_length=10, choices=STATUS, default="pending")
    placed_at     = models.DateTimeField(auto_now_add=True)
    resolved_at   = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Apuesta"
        verbose_name_plural = "Apuestas"
        ordering  = ["-placed_at"]
        indexes   = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["option", "status"]),
        ]

    def __str__(self):
        return f"{self.user.username} | {self.option.group_name} @{self.odds_at_bet} | {self.status}"

    def save(self, *args, **kwargs):
        self.potential_win = round(self.amount * self.odds_at_bet, 2)
        super().save(*args, **kwargs)
