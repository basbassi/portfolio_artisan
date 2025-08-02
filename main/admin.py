from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Category, Product, Profile, Metier

@admin.register(Metier)
class MetierAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'metier')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'artisan', 'category')
    list_filter = ('category', 'artisan')
    search_fields = ('name', 'description')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'metier', 'telephone', 'cover_photo_preview')
    search_fields = ('user__username', 'metier__name', 'telephone')
    readonly_fields = ('cover_photo_preview',)
    
    def cover_photo_preview(self, obj):
        if obj.cover_photo:
            return mark_safe(f'<img src="{obj.cover_photo.url}" style="max-height: 100px; max-width: 100px;" />')
        return "Aucune image"
    cover_photo_preview.short_description = 'Aperçu photo de couverture'