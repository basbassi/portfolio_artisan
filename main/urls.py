from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import congratulations
from .views import download_qr_code
from .views import contact_artisan

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-product/', views.add_product, name='add_product'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('<username>/contact/', contact_artisan, name='contact_artisan'),
    path('generate-card/', views.generate_business_card, name='generate_business_card'),
    path('change-template/', views.change_template, name='change_template'),
    path('download-qr-code/', download_qr_code, name='download_qr_code'),
    path('congratulations/', congratulations, name='congratulations'),
    path('<username>/', views.presentation, name='presentation'),
    path('<username>/category/<int:category_id>/', views.products_by_category, name='products_by_category'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('product/<int:product_id>/edit/', views.edit_product, name='edit_product'),
    path('<username>/product/<int:product_id>/', views.product_detail, name='product_detail'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)