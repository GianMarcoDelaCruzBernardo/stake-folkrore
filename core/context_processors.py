from contests.models import Contest


def global_context(request):
    try:
        active_contests = list(
            Contest.objects
            .filter(status="active", is_active=True)
            .only("id", "name", "slug")[:3]
        )
    except Exception:
        active_contests = []
    return {
        "active_contests_nav": active_contests,
        "SITE_NAME": "StakeFolclor",
    }