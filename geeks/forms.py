from django import forms


class GeeksForm(forms.Form):
    image = forms.ImageField()