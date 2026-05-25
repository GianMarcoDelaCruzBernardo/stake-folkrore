from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from contests.models import Contest
from .models import Wallet, BetOption, Bet
from .services import place_bet as svc_place_bet, get_wallet


@login_required
def bet_contest_list(request):
    contests = Contest.objects.filter(is_active=True, status__in=["upcoming", "active", "final"])
    wallet = get_wallet(request.user)
    return render(request, "bets/contest_list.html", {"contests": contests, "wallet": wallet})


@login_required
def bet_lobby(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    wallet  = get_wallet(request.user)

    # Opciones abiertas por bloque
    open_block_opts = (
        BetOption.objects
        .filter(contest=contest, bet_type="block_qualifier", is_active=True, is_resolved=False)
        .select_related("block")
        .order_by("block__order", "group_name")
    )
    blocks_map = {}
    for opt in open_block_opts:
        k = opt.block_id
        if k not in blocks_map:
            blocks_map[k] = {"block": opt.block, "options": []}
        blocks_map[k]["options"].append(opt)
    block_groups = list(blocks_map.values())

    # Opciones resueltas (para mostrar resultados)
    resolved_block_opts = (
        BetOption.objects
        .filter(contest=contest, bet_type="block_qualifier", is_resolved=True)
        .select_related("block")
        .order_by("block__order", "group_name")
    )

    # Campeon abierto / resuelto
    champ_open     = BetOption.objects.filter(contest=contest, bet_type="champion", is_active=True,  is_resolved=False).order_by("odds")
    champ_resolved = BetOption.objects.filter(contest=contest, bet_type="champion", is_resolved=True).order_by("odds")

    # Mis tickets en este concurso
    my_bets_qs = (
        Bet.objects
        .filter(user=request.user, option__contest=contest)
        .select_related("option", "option__block")
        .order_by("-placed_at")
    )
    my_pending = my_bets_qs.filter(status="pending")
    my_resolved = my_bets_qs.exclude(status="pending")

    ctx = {
        "contest": contest,
        "wallet": wallet,
        "block_groups": block_groups,
        "resolved_block_opts": resolved_block_opts,
        "champ_open": champ_open,
        "champ_resolved": champ_resolved,
        "my_pending": my_pending,
        "my_resolved": my_resolved,
        "has_open": len(block_groups) > 0 or champ_open.exists(),
    }
    return render(request, "bets/lobby.html", ctx)


@login_required
@transaction.atomic
def place_bet_view(request, option_id):
    opt = get_object_or_404(BetOption, pk=option_id)
    if request.method != "POST":
        return redirect("bets:lobby", slug=opt.contest.slug)

    bet, error = svc_place_bet(request.user, opt, request.POST.get("amount", ""))
    if error:
        messages.error(request, error)
    else:
        messages.success(
            request,
            f"Ticket registrado: {opt.group_name} @{opt.odds} — "
            f"Ganancia potencial S/{bet.potential_win}. Saldo: S/{get_wallet(request.user).balance:.2f}."
        )
    return redirect("bets:lobby", slug=opt.contest.slug)


@login_required
def my_bets(request):
    wallet  = get_wallet(request.user)
    pending = (
        Bet.objects.filter(user=request.user, status="pending")
        .select_related("option", "option__contest", "option__block")
        .order_by("-placed_at")
    )
    resolved = (
        Bet.objects.filter(user=request.user).exclude(status="pending")
        .select_related("option", "option__contest", "option__block")
        .order_by("-placed_at")
    )
    return render(request, "bets/my_bets.html", {
        "wallet": wallet,
        "pending": pending,
        "resolved": resolved,
    })
