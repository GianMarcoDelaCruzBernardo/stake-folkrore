from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from bets.services import get_wallet
from .models import StoreItem, Redemption
from .forms import RedemptionForm
from .services import redeem_item


def store_list(request):
    """Lista publica de premios disponibles."""
    items  = StoreItem.objects.filter(is_active=True).order_by("order", "price")
    wallet = get_wallet(request.user) if request.user.is_authenticated else None
    return render(request, "store/store_list.html", {
        "items":  items,
        "wallet": wallet,
    })


@login_required
def redeem_view(request, item_id):
    """
    Muestra el formulario de canje y procesa el POST.
    El boton de canje solo aparece si el usuario tiene saldo suficiente
    (verificado en template Y en servicio).
    """
    item   = get_object_or_404(StoreItem, pk=item_id, is_active=True)
    wallet = get_wallet(request.user)

    # Verificar si ya tiene un canje pendiente o aprobado de este item
    already = Redemption.objects.filter(
        user=request.user,
        item=item,
        status__in=["pending", "approved"],
    ).exists()

    if request.method == "POST":
        form = RedemptionForm(request.POST)
        if form.is_valid():
            redemption, error = redeem_item(
                user=request.user,
                item=item,
                form_data=form.cleaned_data,
            )
            if error:
                messages.error(request, error)
            else:
                messages.success(
                    request,
                    f"Solicitud enviada correctamente. "
                    f"Revisaremos tu canje de '{item.name}' pronto."
                )
                return redirect("store:my_redemptions")
    else:
        form = RedemptionForm()

    return render(request, "store/redeem.html", {
        "item":    item,
        "wallet":  wallet,
        "form":    form,
        "can_redeem": wallet.balance >= item.price if wallet else False,
        "already": already,
    })


@login_required
def my_redemptions(request):
    """Historial de canjes del usuario."""
    wallet      = get_wallet(request.user)
    redemptions = (
        Redemption.objects
        .filter(user=request.user)
        .select_related("item")
        .order_by("-created_at")
    )
    return render(request, "store/my_redemptions.html", {
        "redemptions": redemptions,
        "wallet":      wallet,
    })