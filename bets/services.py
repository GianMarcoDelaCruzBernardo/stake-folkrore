"""
bets/services.py
================
Logica de negocio de apuestas. Separada del modelo.
"""
from __future__ import annotations
from decimal import Decimal, InvalidOperation
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

MIN_BET = Decimal("1.00")
MAX_BET = Decimal("500.00")


def place_bet(user, bet_option, amount_raw: str):
    """
    Procesa una apuesta con lock atomico para evitar race condition
    de saldo (doble apuesta simultanea).
    Retorna (bet_instance, None) si exitoso.
    Retorna (None, error_str) si falla.
    """
    from bets.models import Wallet, Bet

    try:
        amount = Decimal(str(amount_raw).strip().replace(",", "."))
    except (InvalidOperation, ValueError):
        return None, "Monto invalido."

    if amount < MIN_BET:
        return None, f"El minimo es S/{MIN_BET}."
    if amount > MAX_BET:
        return None, f"El maximo es S/{MAX_BET}."

    if not bet_option.is_active:
        return None, "Este mercado esta cerrado."
    if bet_option.is_resolved:
        return None, "Este mercado ya fue resuelto."

    with transaction.atomic():
        wallet, _ = Wallet.objects.select_for_update().get_or_create(
            user=user,
            defaults={"balance": Decimal("50.00")},
        )
        if wallet.balance < amount:
            return None, f"Saldo insuficiente. Tienes S/{wallet.balance:.2f}."

        wallet.balance -= amount
        wallet.save(update_fields=["balance"])

        bet = Bet.objects.create(
            user=user,
            option=bet_option,
            amount=amount,
            odds_at_bet=bet_option.odds,
        )

    logger.info("Apuesta creada: user=%s opt=%s amount=%s", user, bet_option, amount)
    return bet, None


def get_wallet(user):
    from bets.models import Wallet
    wallet, _ = Wallet.objects.get_or_create(
        user=user, defaults={"balance": Decimal("50.00")}
    )
    return wallet