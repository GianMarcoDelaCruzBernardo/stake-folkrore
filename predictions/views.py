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
                        prediction=pred, category="block_qualifier",
                        block=block, predicted_group_name=name, position=i,
                    )
        for cat, key in [("champion", "champion"), ("top3", "top3_1"),
                         ("top3", "top3_2"), ("top3", "top3_3")]:
            if cat == "champion":
                n = request.POST.get("champion", "").strip()
                if n:
                    PredictionItem.objects.create(prediction=pred, category="champion", predicted_group_name=n)
            else:
                pos = int(key[-1])
                n = request.POST.get(key, "").strip()
                if n:
                    PredictionItem.objects.create(prediction=pred, category="top3", predicted_group_name=n, position=pos)
        messages.success(request, "Prediccion guardada.")
        return redirect("predictions:my_predictions")

    return render(request, "predictions/make_prediction.html", {
        "contest": contest, "blocks": blocks,
        "prediction": pred, "qualifiers_range": qrange,
    })


@login_required
def my_predictions(request):
    preds = (
        Prediction.objects
        .filter(user=request.user)
        .select_related("contest")
        .prefetch_related("items", "items__block")
        .order_by("-created_at")
    )
    return render(request, "predictions/my_predictions.html", {"predictions": preds})
