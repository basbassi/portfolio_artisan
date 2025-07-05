from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Category, Metier

from django import forms
from django.contrib.auth.models import User
from .models import Product, Category, Metier

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmer mot de passe', widget=forms.PasswordInput)
    telephone = forms.CharField(label='Téléphone')
    whatsapp = forms.CharField(label='Numéro WhatsApp')  # ✅ Ajout du champ
    metier = forms.ModelChoiceField(label='Métier', queryset=Metier.objects.all())
    photo = forms.ImageField(label='Photo de profil', required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            profile = user.profile  # ⚠️ Nécessite que le signal post_save crée bien un profil
            profile.telephone = self.cleaned_data['telephone']
            profile.whatsapp = self.cleaned_data['whatsapp']  # ✅ Enregistrement du numéro WhatsApp
            profile.metier = self.cleaned_data['metier']
            profile.photo = self.cleaned_data.get('photo')
            profile.save()
        return user

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'image']  # ← Enlève 'tags'
