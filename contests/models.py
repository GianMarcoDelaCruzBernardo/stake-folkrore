"""
contests/models.py
==================
Modelos de concursos y scoring. Logica en services.py.
"""
from cloudinary.models import CloudinaryField
from django.db import models


class Contest(models.Model):
    STATUS = [
        ("upcoming",  "Proximo"),
        ("active",    "En Curso"),
        ("final",     "En Final"),
        ("finished",  "Finalizado"),
    ]
    name                  = models.CharField(max_length=200, verbose_name="Nombre")
    slug                  = models.SlugField(unique=True)
    description           = models.TextField(blank=True)
    flyer                 = CloudinaryField('flyer', null=True, blank=True)
    location              = models.CharField(max_length=200)
    date                  = models.DateField()
    status                = models.CharField(max_length=20, choices=STATUS, default="upcoming")
    judges_count          = models.PositiveIntegerField(default=4, verbose_name="Jurados en bloques")
    final_judges_count    = models.PositiveIntegerField(default=4, verbose_name="Jurados en final")
    qualifiers_per_block  = models.PositiveIntegerField(default=2, verbose_name="Clasificados por bloque")
    is_active             = models.BooleanField(default=True)
    created_at            = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Concurso"
        verbose_name_plural = "Concursos"
        ordering = ["-date"]

    def __str__(self):
        return self.name

    def get_blocks(self):
        return self.blocks.filter(is_active=True, is_final=False).order_by("order")


class Block(models.Model):
    contest  = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="blocks")
    name     = models.CharField(max_length=100)
    order    = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    is_final = models.BooleanField(default=False, verbose_name="Es bloque final")

    class Meta:
        verbose_name = "Bloque"
        verbose_name_plural = "Bloques"
        ordering = ["order"]

    def __str__(self):
        return f"{self.contest.name} — {self.name}"

    def get_groups(self):
        return self.groups.all().order_by("order")


class Group(models.Model):
    block     = models.ForeignKey(Block, on_delete=models.CASCADE, related_name="groups")
    name      = models.CharField(max_length=200, verbose_name="Nombre agrupacion")
    logo      = models.ImageField(upload_to="logos/", null=True, blank=True)
    order     = models.PositiveIntegerField(default=1, verbose_name="Orden")
    qualified = models.BooleanField(default=False, verbose_name="Clasificado")

    class Meta:
        verbose_name = "Agrupacion"
        verbose_name_plural = "Agrupaciones"
        ordering = ["order"]

    def __str__(self):
        return f"{self.name} ({self.block.name})"

    def get_total_score(self):
        return sum(s.score for s in self.scores.all())

    def get_scores_list(self, n):
        d = {s.judge_number: s.score for s in self.scores.all()}
        return [d.get(i) for i in range(1, n + 1)]


class Judge(models.Model):
    contest      = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="judges")
    name         = models.CharField(max_length=200)
    judge_number = models.PositiveIntegerField()

    class Meta:
        verbose_name = "Jurado"
        verbose_name_plural = "Jurados"
        ordering = ["judge_number"]

    def __str__(self):
        return f"PJ{self.judge_number} — {self.name}"


class Score(models.Model):
    group        = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="scores")
    judge_number = models.PositiveIntegerField()
    score        = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Puntaje"
        verbose_name_plural = "Puntajes"
        unique_together = ("group", "judge_number")
        ordering = ["judge_number"]

    def __str__(self):
        return f"{self.group.name} PJ{self.judge_number}: {self.score}"


class FinalGroup(models.Model):
    contest      = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="final_groups")
    source_group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True, related_name="final_entries")
    name         = models.CharField(max_length=200)
    logo         = models.ImageField(upload_to="final_logos/", null=True, blank=True)
    final_order  = models.PositiveIntegerField(default=1, verbose_name="Orden en final (sorteo)")

    class Meta:
        verbose_name = "Agrupacion en Final"
        verbose_name_plural = "Tabla Final"
        ordering = ["final_order"]
        unique_together = ("contest", "name")

    def __str__(self):
        return f"{self.name} (Final — {self.contest.name})"

    def get_total_score(self):
        return sum(s.score for s in self.final_scores.all())

    def get_scores_list(self, n):
        d = {s.judge_number: s.score for s in self.final_scores.all()}
        return [d.get(i) for i in range(1, n + 1)]


class FinalScore(models.Model):
    final_group  = models.ForeignKey(FinalGroup, on_delete=models.CASCADE, related_name="final_scores")
    judge_number = models.PositiveIntegerField()
    score        = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Puntaje Final"
        verbose_name_plural = "Puntajes Final"
        unique_together = ("final_group", "judge_number")
        ordering = ["judge_number"]

    def __str__(self):
        return f"{self.final_group.name} PJ{self.judge_number}: {self.score}"


class FinalResult(models.Model):
    contest     = models.ForeignKey(Contest, on_delete=models.CASCADE, related_name="final_results")
    group_name  = models.CharField(max_length=200)
    group_logo  = models.ImageField(upload_to="final_logos/", null=True, blank=True)
    position    = models.PositiveIntegerField()
    total_score = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "Resultado Final"
        verbose_name_plural = "Podio Final"
        ordering = ["position"]

    def __str__(self):
        return f"#{self.position} {self.group_name} — {self.contest.name}"

