from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from contests.models import Contest, Group, Block
from .models import Prediction


def prediction_contest_list(request):
    contests = Contest.objects.filter(
        is_active=True,
        status__in=["active", "final", "finished"]
    ).order_by("-date")
    user_pred_ids = []
    if request.user.is_authenticated:
        user_pred_ids = list(
            Prediction.objects.filter(user=request.user)
            .values_list("contest_id", flat=True)
        )
    return render(request, "predictions/contest_list.html", {
        "contests":      contests,
        "user_pred_ids": user_pred_ids,
    })


@login_required
def vote(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    block_ids = Block.objects.filter(contest=contest, is_active=True).values_list("id", flat=True)
    groups = Group.objects.filter(block__in=block_ids).order_by("block__order", "order")
    pred = Prediction.objects.filter(user=request.user, contest=contest).first()
    total_votes = Prediction.objects.filter(contest=contest).exclude(champion=None).count()
    group_votes = []
    for g in groups:
        votes = Prediction.objects.filter(contest=contest, champion=g).count()
        pct = round(votes / total_votes * 100) if total_votes > 0 else 0
        group_votes.append({
            "group":  g,
            "votes":  votes,
            "pct":    pct,
            "chosen": pred.champion_id == g.pk if pred else False,
        })
    return render(request, "predictions/vote.html", {
        "contest":     contest,
        "group_votes": group_votes,
        "prediction":  pred,
        "total_votes": total_votes,
    })


@login_required
@require_POST
def submit_vote(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    group_id = request.POST.get("group_id")
    block_ids = Block.objects.filter(contest=contest, is_active=True).values_list("id", flat=True)
    group = get_object_or_404(Group, pk=group_id, block__in=block_ids)
    pred, _ = Prediction.objects.get_or_create(user=request.user, contest=contest)
    pred.champion = group
    pred.save(update_fields=["champion", "updated_at"])
    return redirect("predictions:vote", slug=slug)


@login_required
def my_predictions(request):
    preds = (
        Prediction.objects
        .filter(user=request.user)
        .select_related("contest", "champion")
        .prefetch_related("contest__final_results")
        .order_by("-created_at")
    )
    return render(request, "predictions/my_predictions.html", {"predictions": preds})
