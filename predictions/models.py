from django.db import models
from django.conf import settings
from contests.models import Contest, Block, Group


def _n(s):
    return s.strip().lower()


class Prediction(models.Model):
    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="predictions")
    contest   = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="predictions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Prediccion"
        verbose_name_plural = "Predicciones"
        unique_together = ("user", "contest")

    def __str__(self):
        return f"{self.user.username} — {self.contest.name}"

    def get_accuracy(self):
        items = list(self.items.all())
        resolved = [it for it in items if it.status() != "pending"]
        if not resolved:
            return None
        correct = sum(1 for it in resolved if it.status() == "correct")
        return round(correct / len(resolved) * 100)

    def counts(self):
        items = list(self.items.all())
        resolved = [it for it in items if it.status() != "pending"]
        correct  = sum(1 for it in resolved if it.status() == "correct")
        wrong    = len(resolved) - correct
        pending  = len(items) - len(resolved)
        return {"correct": correct, "wrong": wrong, "pending": pending, "total": len(items)}


class PredictionItem(models.Model):
    CAT = [
        ("block_qualifier", "Clasificado de Bloque"),
        ("champion",        "Campeon"),
        ("top3",            "Top 3"),
    ]
    prediction           = models.ForeignKey(Prediction, on_delete=models.CASCADE, related_name="items")
    category             = models.CharField(max_length=30, choices=CAT)
    block                = models.ForeignKey(Block, on_delete=models.SET_NULL, null=True, blank=True)
    predicted_group_name = models.CharField(max_length=200)
    position             = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        verbose_name = "Item de Prediccion"
        verbose_name_plural = "Items de Prediccion"

    def __str__(self):
        return f"{self.prediction.user.username} | {self.get_category_display()}: {self.predicted_group_name}"

    def is_correct(self):
        contest = self.prediction.contest
        name = _n(self.predicted_group_name)

        if self.category == "block_qualifier" and self.block_id:
            qs = Group.objects.filter(block_id=self.block_id, qualified=True)
            if not qs.exists():
                return None
            return name in [_n(g.name) for g in qs]

        if self.category == "champion":
            r = contest.final_results.filter(position=1).first()
            if not r:
                return None
            return _n(r.group_name) == name

        if self.category == "top3":
            qs = contest.final_results.filter(position__lte=3)
            if not qs.exists():
                return None
            return name in [_n(r.group_name) for r in qs]

        return None

    def status(self):
        r = self.is_correct()
        if r is None:
            return "pending"
        return "correct" if r else "wrong"
