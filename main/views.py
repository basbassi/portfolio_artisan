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
            return redirect('add_product')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

from .models import Profile  # Assure-toi d'avoir cette ligne en haut

from django.core.paginator import Paginator

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Profile
from .forms import ProductForm
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
import qrcode


    
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django_countries import countries

# ... votre code existant ...

from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def update_profile(request):
    try:
        user = request.user
        profile = user.profile
        
        # ✅ Mise à jour User
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        # ✅ Mise à jour Profile
        profile.telephone = request.POST.get('telephone', profile.telephone)
        profile.ville = request.POST.get('ville', profile.ville)
        profile.adresse = request.POST.get('adresse', profile.adresse)  # ✅ Nouveau
        
        # ✅ Photo de profil
        if 'photo' in request.FILES:
            profile.photo = request.FILES['photo']
        
        profile.save()
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})



# Modifiez votre vue dashboard existante pour inclure les pays
@login_required
def dashboard(request):
    profile = request.user.profile
    products = Product.objects.filter(artisan=request.user).order_by('-created_at')
    categories = Category.objects.filter(metier=profile.metier) if profile.metier else Category.objects.none()
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        form.fields['category'].queryset = categories
        if form.is_valid():
            product = form.save(commit=False)
            product.artisan = request.user
            product.save()
            messages.success(request, "Produit ajouté avec succès!")
            return redirect('dashboard')
    else:
        form = ProductForm()
        form.fields['category'].queryset = categories
    
    context = {
        'form': form,
        'products': products,
        'completion': profile.profile_completion,
        'countries': countries,  # Nouveau champ ajouté
    }
    return render(request, 'dashboard.html', context)

def calculate_profile_completion(profile):
    """Calcule le pourcentage de complétion du profil"""
    fields = ['telephone', 'metier', 'photo', 'ville', 'pays']
    completed = sum(1 for field in fields if getattr(profile, field))
    return int((completed / len(fields)) * 100)

from django.http import Http404

def presentation(request, username):
    user = get_object_or_404(User, username=username)
    categories = Category.objects.filter(product__artisan=user).distinct()

    for category in categories:
        # Récupérer le premier produit avec image dans cette catégorie
        product_with_image = Product.objects.filter(
            artisan=user,
            category=category,
            image__isnull=False
        ).first()

        # Ajouter l'URL de l'image à la catégorie
        if product_with_image and product_with_image.image:
            category.preview_image = product_with_image.image
        else:
            category.preview_image = None

    return render(request, 'presentation.html', {
        'artisan': user,
        'categories': categories
    })


# Dans views.py
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import User, Category, Product

def products_by_category(request, username, category_id):
    try:
        artisan = get_object_or_404(User, username=username)
        category = get_object_or_404(Category, id=category_id)
        products = Product.objects.filter(artisan=artisan, category=category)
        
        return render(request, 'products_by_category.html', {
            'artisan': artisan,
            'category': category,
            'products': products
        })
    except Exception as e:
        raise Http404("La page demandée n'existe pas")
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

from django.views.decorators.http import require_http_methods

from django.shortcuts import redirect

@login_required
def congratulations(request):
    """Page intermédiaire avant la présentation"""
    profile = request.user.profile
    if not profile.has_seen_congrats:
        profile.has_seen_congrats = True
        profile.save()
        return render(request, 'congratulations.html')
    return redirect('presentation', username=request.user.username)


from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, black, white
from django.contrib.auth.decorators import login_required
from io import BytesIO
import qrcode
from reportlab.lib.utils import ImageReader

@login_required
def generate_business_card(request):
    profile = request.user.profile

    # --- Dimensions ---
    card_width = 90 * mm
    card_height = 52 * mm

    # --- Couleurs ---
    primary_color = HexColor("#BBAAB7")   # bandeau sombre en haut
    accent_color = HexColor("#007ACC")    # couleur du texte titre
    background_color = HexColor("#AAEBE7")  # fond clair

    # --- Buffer PDF ---
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(card_width, card_height))

    # --- Fond général ---
    p.setFillColor(background_color)
    p.rect(0, 0, card_width, card_height, fill=1, stroke=0)

    # --- Bandeau en haut ---
    p.setFillColor(primary_color)
    p.rect(0, card_height - 12 * mm, card_width, 12 * mm, fill=1, stroke=0)

    # --- Texte sur le bandeau ---
    p.setFont("Helvetica-Bold", 12)
    p.setFillColor(white)
    title_text = profile.metier.name.upper() if getattr(profile, "metier", None) else "PROFESSIONNEL"
    p.drawCentredString(card_width / 2, card_height - 8 * mm, title_text)

    # --- Nom complet ---
    full_name = (profile.user.get_full_name() or profile.user.username).upper()
    p.setFont("Helvetica-Bold", 14)
    p.setFillColor(black)
    p.drawCentredString(card_width / 2, card_height - 18 * mm, full_name)

    # --- Localisation ---
    ville = profile.ville or "VILLE"
    pays = profile.pays.name.upper() if getattr(profile, "pays", None) else "PAYS"
    location = f"{ville.upper()}, {pays}"
    p.setFont("Helvetica", 9)
    p.drawCentredString(card_width / 2, card_height - 23 * mm, location)

    # --- QR Code ---
    qr_data = profile.share_link or "https://votresite.com"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    qr_image_reader = ImageReader(qr_buffer)
    qr_size = 14 * mm
    p.drawImage(qr_image_reader, card_width - qr_size - 8 * mm, 6 * mm, width=qr_size, height=qr_size, mask='auto')

    # --- Coordonnées ---
    telephone = profile.telephone or "Téléphone"
    email = profile.user.email or "Email"
    share_link = profile.share_link or "Lien"
    adresse = profile.adresse or "Adresse non renseignée"

    contact_info = [
        ("static/icons/phone.png", telephone),
        ("static/icons/link.png", share_link),
        ("static/icons/localisation.png", adresse),
        ("static/icons/gmail.png", email),
    ]

    # --- Position de départ ---
    start_x = 8 * mm
    start_y = card_height - 30 * mm

    p.setFont("Helvetica", 8)
    for i, (icon_path, text) in enumerate(contact_info):
        y_pos = start_y - (i * 6 * mm)

        # Icône
        try:
            icon_img = ImageReader(icon_path)
            p.drawImage(icon_img, start_x, y_pos, width=4 * mm, height=4 * mm, mask='auto')
        except:
            pass  # ignore si l'icône est manquante

        # Texte à côté de l'icône
        p.setFillColor(black)
        p.drawString(start_x + 6 * mm, y_pos + 1 * mm, text)

    # --- Encadrement optionnel ---
    p.setStrokeColor(primary_color)
    p.setLineWidth(1)
    p.rect(1 * mm, 1 * mm, card_width - 2 * mm, card_height - 2 * mm, stroke=1, fill=0)

    # --- Finalisation ---
    p.showPage()
    p.save()

    pdf = buffer.getvalue()
    buffer.close()
    qr_buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="carte_visite_{request.user.username}.pdf"'
    return response




from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category
from .forms import ProductForm

@login_required
def add_product(request):
    profile = request.user.profile
    categories = Category.objects.filter(metier=profile.metier) if profile.metier else Category.objects.none()
    existing_count = Product.objects.filter(artisan=request.user).count()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        form.fields['category'].queryset = categories
        
        if form.is_valid():
            product = form.save(commit=False)
            product.artisan = request.user
            product.save()
            
            messages.success(request, "Produit ajouté avec succès !")
            
            # Si l'utilisateur clique sur "Enregistrer et aller au Dashboard"
            if 'go_to_dashboard' in request.POST:
                return redirect('dashboard')
            # Sinon (bouton "Ajouter et continuer"), reste sur la page
            return redirect('add_product')
    else:
        form = ProductForm()
        form.fields['category'].queryset = categories

    context = {
        'form': form,
        'existing_count': existing_count,
    }
    return render(request, 'add_product.html', context)
from django.http import HttpResponse
import qrcode
from io import BytesIO
from django.contrib.auth.decorators import login_required

@login_required
def download_qr_code(request):
    """Génère et télécharge uniquement le QR code du lien de partage"""
    profile = request.user.profile
    qr_data = profile.share_link or "https://votresite.com"
    
    # Création du QR code avec un design légèrement amélioré
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # Correction haute
        box_size=12,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    # Création de l'image avec un contraste amélioré
    img = qr.make_image(fill_color="#2c3e50", back_color="#ffffff")  # Couleur foncée sur fond blanc
    
    # Conversion en réponse HTTP
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    response = HttpResponse(buffer, content_type='image/png')
    response['Content-Disposition'] = f'attachment; filename="QRCode_{request.user.username}.png"'
    return response

# In your views.py
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse

def contact_artisan(request, username):
    if request.method == 'POST':
        try:
            artisan = User.objects.get(username=username)
            name = request.POST.get('name')
            email = request.POST.get('email')
            subject = request.POST.get('subject')
            message = request.POST.get('message')
            
            # Send email to artisan
            send_mail(
                f"Message from {name}: {subject}",
                f"From: {name} <{email}>\n\n{message}",
                settings.DEFAULT_FROM_EMAIL,
                [artisan.email],
                fail_silently=False,
            )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})