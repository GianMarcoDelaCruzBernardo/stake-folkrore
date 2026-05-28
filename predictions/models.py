from django.db import models
from django.conf import settings
from contests.models import Contest, FinalGroup


class Prediction(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="predictions")
    contest    = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="predictions")
    champion   = models.ForeignKey(FinalGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name="champion_predictions")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = "Prediccion"
        verbose_name_plural = "Predicciones"
        unique_together     = ("user", "contest")

    def __str__(self):
        champ = self.champion.name if self.champion else "Sin votar"
        return f"{self.user.username} — {self.contest.name} — {champ}"

    def is_correct(self):
        result = self.contest.final_results.filter(position=1).first()
        if not result or not self.champion:
            return None
        return result.group_name.strip().lower() == self.champion.name.strip().lower()

    def status(self):
        r = self.is_correct()
        if r is None:
            return "pending"
        return "correct" if r else "wrong"