from contests.models import Contest


def global_context(request):
    active_contests = Contest.objects.filter(status='active', is_active=True)[:3]
    return {
        'active_contests_nav': active_contests,
        'SITE_NAME': 'StakeFolclor',
    }
