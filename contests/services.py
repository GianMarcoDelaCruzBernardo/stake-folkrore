"""
contests/services.py
====================
Toda la logica de negocio del sistema de concursos.
Views y signals solo llaman a estos metodos.
"""
from __future__ import annotations
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


def calculate_champion_odds(score: int, all_scores: list) -> Decimal:
    """
    Cuota del campeon basada en puntaje relativo.
    Mayor puntaje = favorito = cuota baja (1.20).
    Menor puntaje = outsider = cuota alta (2.00).
    """
    if not all_scores or max(all_scores) == 0:
        return Decimal("1.80")
    max_s = max(all_scores)
    min_s = min(all_scores)
    if max_s == min_s:
        return Decimal("1.53")
    ratio = (score - min_s) / (max_s - min_s)
    raw = Decimal("2.00") - Decimal(str(round(ratio * 0.80, 2)))
    return max(Decimal("1.20"), min(Decimal("2.00"), round(raw, 2)))


def add_group_to_final(group) -> None:
    """
    Agrega una agrupacion clasificada a FinalGroup.
    Idempotente: no duplica si ya existe.
    """
    from contests.models import FinalGroup
    fg, created = FinalGroup.objects.get_or_create(
        contest=group.block.contest,
        name=group.name,
        defaults={
            "source_group": group,
            "logo": group.logo,
            "final_order": FinalGroup.objects.filter(
                contest=group.block.contest
            ).count() + 1,
        },
    )
    if not created and group.logo and not fg.logo:
        fg.logo = group.logo
        fg.save(update_fields=["logo"])
    logger.info("FinalGroup '%s' -> contest '%s' (created=%s)", group.name, group.block.contest, created)


def rebuild_podium(contest) -> None:
    """
    Recalcula FinalResult completo desde los FinalScore actuales.
    Solo incluye grupos con puntaje > 0.
    """
    from contests.models import FinalGroup, FinalResult
    groups = list(FinalGroup.objects.filter(contest=contest).prefetch_related("final_scores"))
    ranked = sorted(groups, key=lambda fg: fg.get_total_score(), reverse=True)
    FinalResult.objects.filter(contest=contest).delete()
    to_create = []
    for pos, fg in enumerate(ranked, start=1):
        total = fg.get_total_score()
        if total == 0:
            continue
        to_create.append(
            FinalResult(
                contest=contest,
                group_name=fg.name,
                group_logo=fg.logo,
                position=pos,
                total_score=total,
            )
        )
    FinalResult.objects.bulk_create(to_create)
    logger.info("Podio recalculado para '%s': %d posiciones", contest, len(to_create))


def refresh_champion_odds(contest) -> None:
    """
    Recalcula cuotas de campeon basadas en puntajes actuales de FinalGroup.
    Solo actualiza opciones no resueltas.
    """
    from contests.models import FinalGroup
    from bets.models import BetOption
    groups = list(FinalGroup.objects.filter(contest=contest).prefetch_related("final_scores"))
    if not groups:
        return
    scores = [fg.get_total_score() for fg in groups]
    for fg, score in zip(groups, scores):
        new_odds = calculate_champion_odds(score, scores)
        BetOption.objects.filter(
            contest=contest,
            bet_type="champion",
            group_name=fg.name,
            is_resolved=False,
        ).update(odds=new_odds)


def resolve_bets_for_contest(contest) -> dict:
    """
    Resuelve todas las apuestas pendientes de un concurso.
    Usa prefetch para reducir queries en el loop de pago.
    Retorna resumen: {won: N, lost: N}
    """
    from django.utils import timezone
    from bets.models import BetOption, Bet, Wallet

    summary = {"won": 0, "lost": 0}

    def _norm(s: str) -> str:
        return s.strip().lower()

    # Resolver clasificados de bloque
    block_opts = (
        BetOption.objects
        .filter(contest=contest, bet_type="block_qualifier", is_resolved=False)
        .select_related("block")
    )
    for opt in block_opts:
        if not opt.block:
            continue
        from contests.models import Group
        qualified = Group.objects.filter(block=opt.block, qualified=True)
        if not qualified.exists():
            continue
        names = [_norm(g.name) for g in qualified]
        opt.won = _norm(opt.group_name) in names
        opt.is_resolved = True
        opt.is_active = False
        opt.save(update_fields=["won", "is_resolved", "is_active"])

    # Resolver campeon
    champion = contest.final_results.filter(position=1).first()
    if champion:
        champ_opts = BetOption.objects.filter(
            contest=contest, bet_type="champion", is_resolved=False
        )
        for opt in champ_opts:
            opt.won = _norm(opt.group_name) == _norm(champion.group_name)
            opt.is_resolved = True
            opt.is_active = False
            opt.save(update_fields=["won", "is_resolved", "is_active"])

    # Pagar / descontar — prefetch para reducir queries
    resolved_opts = BetOption.objects.filter(
        contest=contest, is_resolved=True, won__isnull=False
    )
    for opt in resolved_opts:
        pending_bets = (
            Bet.objects
            .filter(option=opt, status="pending")
            .select_related("user")
        )
        for bet in pending_bets:
            wallet, _ = Wallet.objects.get_or_create(user=bet.user)
            if opt.won:
                wallet.balance  += bet.potential_win
                wallet.total_won += bet.potential_win
                bet.status = "won"
                summary["won"] += 1
            else:
                wallet.total_lost += bet.amount
                bet.status = "lost"
                summary["lost"] += 1
            bet.resolved_at = timezone.now()
            bet.save(update_fields=["status", "resolved_at"])
            wallet.save(update_fields=["balance", "total_won", "total_lost"])

    logger.info("Apuestas resueltas en '%s': %s", contest, summary)
    return summary


def generate_block_bet_options(contest, activate: bool = False) -> int:
    """
    Crea BetOption (cuota 1.53) para cada agrupacion de cada bloque.
    activate=False: desactivadas hasta que admin las active.
    """
    from bets.models import BetOption
    created = 0
    for block in contest.blocks.filter(is_final=False, is_active=True):
        for group in block.groups.all():
            _, was_new = BetOption.objects.get_or_create(
                contest=contest,
                bet_type="block_qualifier",
                block=block,
                group_name=group.name,
                defaults={
                    "group_logo": group.logo,
                    "odds": Decimal("1.53"),
                    "is_active": activate,
                },
            )
            if was_new:
                created += 1
    logger.info("BetOptions bloques generadas para '%s': %d", contest, created)
    return created


def generate_champion_bet_options(contest, activate: bool = False) -> int:
    """
    Crea BetOption de campeon por cada FinalGroup, con cuota calculada.
    activate=False: el admin las revisa antes de activar.
    """
    from contests.models import FinalGroup
    from bets.models import BetOption
    groups = list(
        FinalGroup.objects
        .filter(contest=contest)
        .prefetch_related("final_scores", "source_group")
    )
    if not groups:
        return 0
    scores = [
        fg.source_group.get_total_score() if fg.source_group else fg.get_total_score()
        for fg in groups
    ]
    created = 0
    for fg, score in zip(groups, scores):
        odds = calculate_champion_odds(score, scores)
        _, was_new = BetOption.objects.get_or_create(
            contest=contest,
            bet_type="champion",
            group_name=fg.name,
            defaults={"group_logo": fg.logo, "odds": odds, "is_active": activate},
        )
        if not was_new:
            BetOption.objects.filter(
                contest=contest,
                bet_type="champion",
                group_name=fg.name,
                is_resolved=False,
            ).update(odds=odds)
        else:
            created += 1
    logger.info("BetOptions campeon generadas para '%s': %d", contest, created)
    return created