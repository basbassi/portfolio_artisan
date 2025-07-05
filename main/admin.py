from django.contrib import admin
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
    list_display = ('user', 'metier', 'telephone')
    search_fields = ('user__username', 'metier__name', 'telephone')
