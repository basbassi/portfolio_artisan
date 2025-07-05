from django.db import models
from django.contrib.auth.models import User

class Metier(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    metier = models.ForeignKey('Metier', on_delete=models.CASCADE, null=True)  # Ajoute null=True

    def __str__(self): 
        return f"{self.name} ({self.metier.name if self.metier else 'Aucun métier'})"


class Product(models.Model):
    artisan = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self): 
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    whatsapp = models.CharField(max_length=20, blank=True, null=True)
    metier = models.ForeignKey(Metier, on_delete=models.SET_NULL, null=True)
    telephone = models.CharField(max_length=20)
    photo = models.ImageField(upload_to='profiles/', null=True, blank=True)

    def __str__(self):
        return self.user.username
