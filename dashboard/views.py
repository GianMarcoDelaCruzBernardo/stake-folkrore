from django.shortcuts import redirect


def dashboard_home(request):
    # El dashboard de usuario era relleno; redirigir a home
    return redirect('core:home')
