# main/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()
# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Metier
import os
from django.conf import settings

@receiver(post_save, sender=Metier)
def set_default_hero_image(sender, instance, created, **kwargs):
    if created and not instance.hero_image:
        # Associez une image par défaut basée sur le nom du métier
        default_images = {
            'menuisier': 'default_hero_images/menuiserie.jpg',
            'plombier': 'default_hero_images/plomberie.jpg',
            # Ajoutez d'autres métiers et leurs images par défaut
        }
        
        for metier_name, image_path in default_images.items():
            if metier_name in instance.name.lower():
                instance.hero_image = image_path
                instance.save()
                break