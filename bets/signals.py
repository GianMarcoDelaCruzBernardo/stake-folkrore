"""
bets/signals.py
===============
Senales: solo detectan eventos y delegan a services.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_wallet_on_register(sender, instance, created, **kwargs):
    if created:
        from bets.models import Wallet
        Wallet.objects.get_or_create(
            user=instance, defaults={"balance": Decimal("50.00")}
        )
        logger.info("Wallet creada para user=%s", instance)


@receiver(post_save, sender="contests.Group")
def on_group_qualified(sender, instance, **kwargs):
    """Al clasificar un grupo: FinalGroup + resolver apuestas existentes."""
    if not instance.qualified:
        return
    from contests.services import add_group_to_final, resolve_bets_for_contest
    add_group_to_final(instance)
    resolve_bets_for_contest(instance.block.contest)


@receiver(post_save, sender="contests.FinalScore")
def on_final_score_saved(sender, instance, **kwargs):
    """Al guardar puntaje final: recalcular podio y cuotas."""
    from contests.services import rebuild_podium, refresh_champion_odds, resolve_bets_for_contest
    contest = instance.final_group.contest
    rebuild_podium(contest)
    refresh_champion_odds(contest)
    resolve_bets_for_contest(contest)
