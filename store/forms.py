from django import forms


class RedemptionForm(forms.Form):
    full_name = forms.CharField(
        label="Nombre completo",
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Como aparece en tu DNI",
        }),
    )
    dni = forms.CharField(
        label="DNI",
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "12345678",
        }),
    )
    phone = forms.CharField(
        label="Celular / Yape",
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "9XXXXXXXX",
        }),
    )
    city = forms.CharField(
        label="Ciudad",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Lima, Trujillo, etc.",
        }),
    )
    district = forms.CharField(
        label="Distrito",
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Miraflores, etc.",
        }),
    )
    address = forms.CharField(
        label="Direccion completa",
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 3,
            "placeholder": "Av. / Jr. / Calle, numero, referencia",
        }),
    )
    notes = forms.CharField(
        label="Notas adicionales (opcional)",
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "rows": 2,
            "placeholder": "Horario de entrega, instrucciones especiales, etc.",
        }),
    )