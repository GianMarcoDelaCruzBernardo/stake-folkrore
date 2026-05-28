from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from contests.models import Contest
from .models import Prediction, PredictionItem


@login_required
def make_prediction(request, slug):
    contest = get_object_or_404(Contest, slug=slug)
    pred, _ = Prediction.objects.get_or_create(user=request.user, contest=contest)
    blocks  = contest.get_blocks().prefetch_related("groups")
    qrange  = range(1, contest.qualifiers_per_block + 1)

    if request.method == "POST":
        pred.items.all().delete()
        for block in blocks:
            for i in qrange:
                name = request.POST.get(f"block_{block.id}_qual_{i}", "").strip()
                if name:
                    PredictionItem.objects.create(
                        prediction=pred,
                        category="block_qualifier",
                        block=block,
                        predicted_group_name=name,
                        position=i,
                    )
        champion_name = request.POST.get("champion", "").strip()
        if champion_name:
            PredictionItem.objects.create(
                prediction=pred,
                category="champion",
                predicted_group_name=champion_name,
            )
        for pos in range(1, 4):
            top_name = request.POST.get(f"top3_{pos}", "").strip()
            if top_name:
                PredictionItem.objects.create(
                    prediction=pred,
                    category="top3",
                    predicted_group_name=top_name,
                    position=pos,
                )
        messages.success(request, "Prediccion guardada.")
        return redirect("predictions:my_predictions")

    return render(request, "predictions/make_prediction.html", {
        "contest": contest,
        "blocks": blocks,
        "prediction": pred,
        "qualifiers_range": qrange,
    })


@login_required
def my_predictions(request):
    preds = (
        Prediction.objects
        .filter(user=request.user)
        .select_related("contest")
        .prefetch_related(
            "items",
            "items__block",
            "contest__final_results",
        )
        .order_by("-created_at")
    )
    return render(request, "predictions/my_predictions.html", {"predictions": preds})