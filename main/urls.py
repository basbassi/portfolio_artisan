from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('<str:username>/category/<int:category_id>/', views.products_by_category, name='products_by_category'),

    # cette ligne DOIT être la dernière :
    path('<str:username>/', views.presentation, name='presentation'),
    path('delete-product/<int:product_id>/', views.delete_product, name='delete_product'),
    path('edit-product/<int:product_id>/', views.edit_product, name='edit_product'),
    path('<str:username>/product/<int:product_id>/', views.product_detail, name='product_detail'),


]
