from django.shortcuts import render, get_object_or_404
from .models import Contest, Group, FinalGroup, FinalResult


def contest_list(request):
    contests = Contest.objects.filter(is_active=True)
    return render(request, "contests/contest_list.html", {"contests": contests})


def contest_detail(request, slug):
    contest = get_object_or_404(Contest, slug=slug, is_active=True)
    jn  = contest.judges_count
    fjn = contest.final_judges_count

    # Bloques normales
    blocks_data = []
    for block in contest.get_blocks().prefetch_related("groups__scores"):
        rows = []
        for g in block.get_groups():
            rows.append({
                "group":  g,
                "scores": g.get_scores_list(jn),
                "total":  g.get_total_score(),
            })
        rows.sort(key=lambda x: x["total"], reverse=True)
        blocks_data.append({"block": block, "groups": rows})

    # Tabla final: todos los clasificados ordenados por total final
    final_qs = (
        FinalGroup.objects
        .filter(contest=contest)
        .prefetch_related("final_scores")
        .order_by("final_order")
    )
    final_rows = []
    for fg in final_qs:
        final_rows.append({
            "fg":     fg,
            "scores": fg.get_scores_list(fjn),
            "total":  fg.get_total_score(),
        })
    final_rows_ranked = sorted(final_rows, key=lambda x: x["total"], reverse=True)

    # Podio
    podium = list(contest.final_results.order_by("position")[:3])

    # Todos los participantes
    all_groups = (
        Group.objects
        .filter(block__contest=contest, block__is_final=False)
        .select_related("block")
        .order_by("block__order", "order")
    )

    ctx = {
        "contest":              contest,
        "blocks_data":          blocks_data,
        "judge_range":          range(1, jn  + 1),
        "final_judge_range":    range(1, fjn + 1),
        "final_rows":           final_rows_ranked,
        "has_final":            final_qs.exists(),
        "podium":               podium,
        "all_groups":           all_groups,
    }
    return render(request, "contests/contest_detail.html", ctx)
