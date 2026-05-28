"""
store/services.py
=================
Logica de negocio del canje. Atomica para evitar saldo negativo.
"""
from __future__ import annotations
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)


def redeem_item(user, item, form_data: dict):
    """
    Intenta canjear un premio.
    Descuenta el saldo con lock para evitar doble canje simultaneo.
    Retorna (redemption, None) si OK.
    Retorna (None, mensaje_error) si falla.
    """
    from bets.models import Wallet
    from store.models import Redemption

    if not item.is_active:
        return None, "Este premio no esta disponible."

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(
            user=user,
            defaults={"balance": Decimal("50.00")},
        )

        if wallet.balance < item.price:
            return None, (
                f"Saldo insuficiente. Necesitas S/{item.price:.2f} "
                f"y tienes S/{wallet.balance:.2f}."
            )

        # Verificar stock de nuevo dentro del lock
        if item.stock > 0:
            canjes_aprobados = Redemption.objects.filter(
                item=item, status__in=["pending", "approved"]
            ).count()
            if canjes_aprobados >= item.stock:
                return None, "Este premio ya no tiene stock disponible."

        # Descontar saldo
        wallet.balance -= item.price
        wallet.save(update_fields=["balance"])

        # Crear solicitud
        redemption = Redemption.objects.create(
            user=user,
            item=item,
            cost_paid=item.price,
            status="pending",
            **form_data,
        )

    logger.info(
        "Canje creado: user=%s item=%s cost=%s",
        user, item, item.price,
    )
    return redemption, None


def approve_redemption(redemption):
    """Marca como aprobado. No modifica saldo (ya fue descontado al canjear)."""
    from django.utils import timezone
    redemption.status      = "approved"
    redemption.reviewed_at = timezone.now()
    redemption.save(update_fields=["status", "reviewed_at"])
    logger.info("Canje aprobado: %s", redemption)


def reject_redemption(redemption, admin_notes: str = ""):
    """
    Rechaza el canje y DEVUELVE el saldo al usuario.
    """
    from bets.models import Wallet
    from django.utils import timezone

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(
            user=redemption.user,
            defaults={"balance": Decimal("50.00")},
        )
        wallet.balance += redemption.cost_paid
        wallet.save(update_fields=["balance"])

        redemption.status      = "rejected"
        redemption.admin_notes = admin_notes
        redemption.reviewed_at = timezone.now()
        redemption.save(update_fields=["status", "admin_notes", "reviewed_at"])

    logger.info("Canje rechazado y saldo devuelto: %s", redemption)