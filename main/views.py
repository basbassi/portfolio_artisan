from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm, ProductForm
from .models import Product, Category
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

def home(request):
    return render(request, 'home.html')

from .models import Profile
from .forms import CustomUserCreationForm

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import CustomUserCreationForm, ProductForm
from .models import Product, Category

from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from .models import Profile
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # S'assurer que le profil existe, sinon le créer
            profile, created = Profile.objects.get_or_create(user=user)

            # Remplir les données du profil
            profile.telephone = form.cleaned_data['telephone']
            profile.metier = form.cleaned_data['metier']
            profile.photo = form.cleaned_data.get('photo')
            profile.save()

            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

from .models import Profile  # Assure-toi d'avoir cette ligne en haut

@login_required
def dashboard(request):
    # Assure-toi que le profil existe
    profile, created = Profile.objects.get_or_create(user=request.user)

    products = Product.objects.filter(artisan=request.user)
    categories = Category.objects.filter(metier=profile.metier)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        form.fields['category'].queryset = categories
        if form.is_valid():
            product = form.save(commit=False)
            product.artisan = request.user
            product.save()
            return redirect('dashboard')
    else:
        form = ProductForm()
        form.fields['category'].queryset = categories

    return render(request, 'dashboard.html', {
        'form': form,
        'products': products
    })

from django.http import Http404

def presentation(request, username):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("Utilisateur introuvable.")
    categories = Category.objects.filter(product__artisan=user).distinct()
    return render(request, 'presentation.html', {'artisan': user, 'categories': categories})

def products_by_category(request, username, category_id):
    user = User.objects.get(username=username)
    category = Category.objects.get(id=category_id)
    products = Product.objects.filter(artisan=user, category=category)
    return render(request, 'products_by_category.html', {'category': category, 'products': products, 'artisan': user})
from django.shortcuts import get_object_or_404
from django.contrib import messages

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, artisan=request.user)
    product.delete()
    messages.success(request, "Produit supprimé avec succès.")
    return redirect('dashboard')

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, artisan=request.user)
    profile = request.user.profile
    categories = Category.objects.filter(metier=profile.metier)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        form.fields['category'].queryset = categories
        if form.is_valid():
            form.save()
            messages.success(request, "Produit modifié avec succès.")
            return redirect('dashboard')
    else:
        form = ProductForm(instance=product)
        form.fields['category'].queryset = categories

    return render(request, 'edit_product.html', {
        'form': form,
        'product': product
    })
from django.http import Http404

def product_detail(request, username, product_id):
    try:
        artisan = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("Utilisateur introuvable.")

    product = get_object_or_404(Product, id=product_id, artisan=artisan)

    return render(request, 'product_detail.html', {
        'product': product,
        'artisan': artisan
    })

