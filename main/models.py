from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.utils import timezone
from django.urls import reverse

class Metier(models.Model):
    name = models.CharField(max_length=100)
    hero_image = models.ImageField(upload_to='metier_hero_images/', null=True, blank=True)
    
    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    metier = models.ForeignKey(Metier, on_delete=models.CASCADE, null=True)
    
    def __str__(self): 
        return f"{self.name} ({self.metier.name if self.metier else 'Aucun métier'})"

class Product(models.Model):
    artisan = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    is_featured = models.BooleanField(default=False)
    
    def __str__(self): 
        return self.name
from django.contrib.auth.models import User
from django.db import models
class Profile(models.Model):
    TEMPLATE_CHOICES = [
        ('classic', 'Classique (Bois)'),
        ('modern', 'Moderne'),
        ('minimal', 'Minimaliste'),
        ('elegant', 'Élégant'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    template = models.CharField(
        max_length=20,
        choices=TEMPLATE_CHOICES,
        default='classic'
    )
    
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    metier = models.ForeignKey(Metier, on_delete=models.SET_NULL, null=True)
    telephone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)
    ville = models.CharField(max_length=100, blank=True, null=True)
    pays = CountryField(blank=True, null=True)
    cover_photo = models.ImageField(upload_to='covers/', null=True, blank=True)
    
    # ✅ Nouveau champ adresse
    adresse = models.CharField(max_length=255, blank=True, null=True)

    business_card = models.FileField(upload_to='business_cards/', null=True, blank=True)
    share_link = models.CharField(max_length=255, blank=True)
    has_seen_congrats = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('presentation', kwargs={'username': self.user.username})
    
    def save(self, *args, **kwargs):
        if not self.share_link:
            self.share_link = f"http://votresite.com/{self.user.username}/"
        super().save(*args, **kwargs)
    
    @property
    def profile_completion(self):
        required_fields = ['telephone', 'metier', 'photo', 'ville', 'pays', 'adresse']  # ✅ ajouté adresse
        completed = sum(1 for field in required_fields if getattr(self, field))
        return int((completed / len(required_fields)) * 100)
