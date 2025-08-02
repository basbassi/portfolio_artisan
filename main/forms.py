from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Product, Category, Metier
from django_countries.widgets import CountrySelectWidget
from django import forms
from django.contrib.auth.models import User
from .models import Product, Category, Metier

class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmer mot de passe', widget=forms.PasswordInput)
    telephone = forms.CharField(label='Téléphone')
    whatsapp = forms.CharField(label='Numéro WhatsApp')
    metier = forms.ModelChoiceField(label='Métier', queryset=Metier.objects.all())
    photo = forms.ImageField(label='Photo de profil', required=False)
    ville = forms.CharField(label='Ville')
    pays = forms.CharField(label='Pays')
    
    # ✅ Nouveau champ adresse
    adresse = forms.CharField(label='Adresse complète', required=False)

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
            profile = user.profile
            profile.telephone = self.cleaned_data['telephone']
            profile.whatsapp = self.cleaned_data['whatsapp']
            profile.metier = self.cleaned_data['metier']
            profile.photo = self.cleaned_data.get('photo')
            profile.ville = self.cleaned_data['ville']
            profile.pays = self.cleaned_data['pays']
            
            # ✅ Sauvegarder l’adresse
            profile.adresse = self.cleaned_data.get('adresse')
            
            profile.save()
        return user


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'description', 'image']  # ← Enlève 'tags'
from django import forms
from django.core.validators import RegexValidator

class ContactForm(forms.Form):
    name = forms.CharField(
        label="Votre nom complet",
        max_length=100,
        widget=forms.TextInput(attrs={
            'placeholder': 'Jean Dupont',
            'class': 'form-control'
        })
    )
    
    email = forms.EmailField(
        label="Votre email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'votre@email.com',
            'class': 'form-control'
        })
    )
    
    phone = forms.CharField(
        label="Téléphone (facultatif)",
        required=False,
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?[0-9]{9,15}$',
            message="Format : +123456789 ou 0123456789"
        )],
        widget=forms.TextInput(attrs={
            'placeholder': '+225 0123456789',
            'class': 'form-control'
        })
    )
    
    message = forms.CharField(
        label="Votre message",
        widget=forms.Textarea(attrs={
            'placeholder': 'Décrivez votre projet en détail...',
            'class': 'form-control',
            'rows': 5
        })
    )
# forms.py
# forms.py
from django import forms
from .models import Profile  # Cette ligne est cruciale

class TemplateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['template']
        widgets = {
            'template': forms.RadioSelect(attrs={'class': 'template-radio'}),
        }