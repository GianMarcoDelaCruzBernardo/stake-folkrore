from django.shortcuts import render
from contests.models import Contest


def home(request):
    upcoming = Contest.objects.filter(status='upcoming', is_active=True)[:4]
    active = Contest.objects.filter(status='active', is_active=True)[:4]
    finished = Contest.objects.filter(status='finished', is_active=True)[:4]
    context = {
        'upcoming': upcoming,
        'active': active,
        'finished': finished,
    }
    return render(request, 'core/home.html', context)


def about(request):
    return render(request, 'core/about.html')
