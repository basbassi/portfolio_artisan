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

# views.py
from django.shortcuts import render, get_object_or_404
from django.template.loader import get_template
from django.http import Http404
from .models import User, Profile, Category, Product

def presentation(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile
    
    categories = Category.objects.filter(product__artisan=user).distinct()
    
    # Obtenez l'image hero en fonction du métier
    default_hero = 'static/default_hero.jpg'
    hero_image = profile.metier.hero_image.url if (profile.metier and profile.metier.hero_image) else default_hero
    
    # Préparation des données de catégories
    for category in categories:
        product_with_image = Product.objects.filter(
            artisan=user,
            category=category,
            image__isnull=False
        ).first()
        category.preview_image = product_with_image.image if product_with_image else None

    # Construction du contexte
    context = {
        'artisan': user,
        'categories': categories,
        'hero_image': hero_image,
        'profile': profile  # Ajout du profil au contexte
    }

    # Sélection dynamique du template
    template_name = f"presentation_{profile.template}.html"
    
    try:
        return render(request, template_name, context)
    except:
        # Fallback au template classique si le template spécifié n'existe pas
        return render(request, 'presentation_classic.html', context)


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
from PIL import Image
import qrcode
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import mm
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import ImageReader
from django.contrib.auth.decorators import login_required

@login_required
def generate_business_card(request):
    profile = request.user.profile
    
    # Dimensions standard ISO 7810 ID-1 (carte de visite)
    card_width = 85.6 * mm
    card_height = 53.98 * mm
    margin = 5 * mm
    content_width = card_width - 2 * margin
    
    # Palette de couleurs
    primary_color = (44, 62, 80)    # Bleu foncé (#2C3E50)
    accent_color = (231, 76, 60)    # Rouge (#E74C3C)
    text_color = (51, 51, 51)       # Gris foncé (#333333)
    background_color = (255, 255, 255)  # Blanc
    
    # Création du PDF
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=(card_width, card_height))
    
    # Arrière-plan
    p.setFillColorRGB(*[c/255 for c in background_color])
    p.rect(0, 0, card_width, card_height, fill=True, stroke=False)
    
    # ---- Section Nom et Titre ----
    header_y = card_height - margin - 8 * mm
    
    # Nom complet
    full_name = f"{request.user.first_name or ''} {request.user.last_name or ''}".strip()
    if not full_name:
        full_name = request.user.username
    
    p.setFillColorRGB(*[c/255 for c in primary_color])
    p.setFont("Helvetica-Bold", 14)
    p.drawString(margin, header_y, full_name)
    
    # Métier
    if profile.metier:
        p.setFillColorRGB(*[c/255 for c in accent_color])
        p.setFont("Helvetica-Bold", 10)
        p.drawString(margin, header_y - 6 * mm, profile.metier.name)
    
    # Ligne de séparation
    p.setStrokeColorRGB(*[c/255 for c in accent_color])
    p.setLineWidth(0.25 * mm)
    separator_y = header_y - 9 * mm
    p.line(margin, separator_y, card_width - margin, separator_y)
    
    # ---- Section Coordonnées ----
    contact_y = separator_y - 8 * mm
    line_height = 4 * mm
    
    # Téléphone
    if profile.telephone:
        p.setFillColorRGB(*[c/255 for c in text_color])
        p.setFont("Helvetica", 9)
        p.drawString(margin, contact_y, f"Tél: {profile.telephone}")
        contact_y -= line_height
    
    # Email
    if request.user.email:
        p.setFillColorRGB(*[c/255 for c in text_color])
        p.setFont("Helvetica", 9)
        p.drawString(margin, contact_y, f"Email: {request.user.email}")
        contact_y -= line_height
    
    # Adresse (utilise uniquement les champs existants)
    address_parts = []
    if profile.adresse:
        address_parts.append(profile.adresse)
    if profile.ville:
        address_parts.append(profile.ville)
    if profile.pays:
        address_parts.append(profile.pays.name)
    
    if address_parts:
        p.setFillColorRGB(*[c/255 for c in text_color])
        p.setFont("Helvetica", 9)
        
        # Formatage de l'adresse sur une ou plusieurs lignes
        address_line = ", ".join(address_parts)
        if p.stringWidth(address_line, "Helvetica", 9) < content_width:
            p.drawString(margin, contact_y, address_line)
        else:
            # Si trop long, on split sur plusieurs lignes
            for part in address_parts:
                if contact_y < margin:  # Plus d'espace disponible
                    break
                p.drawString(margin, contact_y, part)
                contact_y -= line_height
    
    # ---- QR Code ----
    qr_size = 18 * mm
    qr_data = profile.share_link or f"https://votresite.com/{request.user.username}"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=6,
        border=1,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    
    qr_img = qr.make_image(fill_color="#2C3E50", back_color="white")
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    p.drawImage(ImageReader(qr_buffer), 
               card_width - margin - qr_size, 
               margin + 5 * mm, 
               width=qr_size, 
               height=qr_size)
    
    # Bordure
    p.setStrokeColorRGB(*[c/255 for c in primary_color])
    p.setLineWidth(0.2 * mm)
    p.rect(margin/2, margin/2, 
           card_width - margin, card_height - margin, 
           stroke=True, fill=False)
    
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
# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import TemplateForm

@login_required
def change_template(request):
    profile = request.user.profile
    if request.method == 'POST':
        form = TemplateForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TemplateForm(instance=profile)
    
    return render(request, 'change_template.html', {'form': form})