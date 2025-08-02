from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Product, Profile, Metier

@admin.register(Metier)
class MetierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'hero_image_preview')
    search_fields = ('name',)
    readonly_fields = ('hero_image_preview',)
    
    def hero_image_preview(self, obj):
        if obj.hero_image:
            return mark_safe(f'<img src="{obj.hero_image.url}" style="max-height: 50px; max-width: 100px;" />')
        return "Aucune image"
    hero_image_preview.short_description = 'Image Hero'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'metier')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'artisan', 'category', 'image_preview')
    list_filter = ('category', 'artisan')
    search_fields = ('name', 'description')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height: 50px; max-width: 50px;" />')
        return "Aucune image"
    image_preview.short_description = 'Aperçu'

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'metier', 'telephone', 'cover_photo_preview', 'photo_preview')
    search_fields = ('user__username', 'metier__name', 'telephone')
    readonly_fields = ('cover_photo_preview', 'photo_preview')
    
    def cover_photo_preview(self, obj):
        if obj.cover_photo:
            return mark_safe(f'<img src="{obj.cover_photo.url}" style="max-height: 50px; max-width: 100px;" />')
        return "Aucune image"
    cover_photo_preview.short_description = 'Cover Preview'
    
    def photo_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" style="max-height: 50px; max-width: 50px; border-radius: 50%;" />')
        return "Aucune image"
    photo_preview.short_description = 'Photo Profil'