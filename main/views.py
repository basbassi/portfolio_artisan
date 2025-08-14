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
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from reportlab.lib.utils import ImageReader
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.units import inch
@login_required
def generate_product_pdf(request, product_id):
    product = get_object_or_404(Product, id=product_id, artisan=request.user)
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=72, leftMargin=72,
                           topMargin=72, bottomMargin=72)
    
    elements = []
    styles = getSampleStyleSheet()
    
    # Style du titre
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1,
        spaceAfter=20
    )
    
    # Titre du document
    elements.append(Paragraph(f"Fiche Produit: {product.name}", title_style))
    
    # Image du produit
    if product.image:
        try:
            # Solution corrigée pour l'image du produit
            img_path = product.image.path
            img = Image(img_path, width=4*inch, height=3*inch)
            img.hAlign = 'CENTER'
            elements.append(img)
            elements.append(Paragraph("<br/><br/>", styles["Normal"]))
        except Exception as e:
            print(f"Erreur chargement image: {e}")
    
    # Données du produit
    product_data = [
        ["Catégorie", product.category.name],
        ["Description", product.description],
        ["Date de création", product.created_at.strftime("%d/%m/%Y")],
        ["Artisan", f"{request.user.get_full_name() or request.user.username}"],
    ]
    
    # Tableau des informations
    table = Table(product_data, colWidths=[2*inch, 4*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor("#4361ee")),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
    ]))
    elements.append(table)
    
    # QR Code - Solution corrigée
    elements.append(Paragraph("<br/><br/><br/>", styles["Normal"]))
    elements.append(Paragraph("Scannez ce QR code pour accéder à mon portfolio:", styles["Normal"]))
    
    qr_data = request.user.profile.share_link or f"https://votresite.com/{request.user.username}/"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    # Utilisation directe du buffer pour l'image
    qr_image = Image(qr_buffer, width=1.5*inch, height=1.5*inch)
    qr_image.hAlign = 'CENTER'
    elements.append(qr_image)
    
    # Génération du PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    qr_buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="fiche_produit_{product.id}.pdf"'
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
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus.flowables import HRFlowable
import qrcode
from .models import Product, Profile

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Table, TableStyle, Image, Spacer
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus.flowables import HRFlowable
import qrcode
from .models import Product, Profile

@login_required
def generate_portfolio_pdf(request):
    products = Product.objects.filter(artisan=request.user).order_by('-created_at')
    profile = request.user.profile
    
    # Création du buffer PDF
    buffer = BytesIO()
    
    # Configuration du document avec marges symétriques
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                          rightMargin=36, leftMargin=36,
                          topMargin=36, bottomMargin=36)
    
    elements = []
    
    # Styles personnalisés
    styles = getSampleStyleSheet()
    
    # Style du titre principal centré
    title_style = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=18,
        leading=22,
        alignment=1,  # Centré
        spaceAfter=20,
        textColor=colors.HexColor('#2b2d42'),
        fontName='Helvetica-Bold'
    )
    
    # Style pour le sous-titre (métier)
    subtitle_style = ParagraphStyle(
        'SubTitle',
        parent=styles['Heading2'],
        fontSize=14,
        leading=18,
        alignment=1,  # Centré
        spaceAfter=24,
        textColor=colors.HexColor('#4361ee'),
        fontName='Helvetica'
    )

    # En-tête avec logo et titre bien alignés
    header_content = []
    
    # Logo centré
    if profile.photo:
        try:
            logo = Image(profile.photo.path, width=1.5*inch, height=1.5*inch)
            logo_table = Table([[logo]], colWidths=[doc.width])
            logo_table.setStyle(TableStyle([
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ]))
            header_content.append(logo_table)
            header_content.append(Spacer(1, 12))
        except:
            pass
    
    # Titre principal centré
    title_text = f"<b>PORTFOLIO DE {request.user.get_full_name().upper() or request.user.username.upper()}</b>"
    header_content.append(Paragraph(title_text, title_style))
    
    # Métier centré
    if profile.metier:
        header_content.append(Paragraph(profile.metier.name.upper(), subtitle_style))
    
    # Ligne de séparation alignée
    header_content.append(HRFlowable(width="100%", thickness=1, lineCap='round', 
                                  color=colors.HexColor("#4361ee"), spaceAfter=24))
    
    elements.extend(header_content)

    # Dimensions fixes pour les images produits
    IMG_WIDTH = 3.5*inch
    IMG_HEIGHT = 2.5*inch
    
    # Liste des produits avec alignement parfait
    for product in products:
        # Tableau pour chaque produit (2 colonnes)
        product_table_data = []
        
        # Colonne image (gauche)
        img_cell = []
        if product.image:
            try:
                img = Image(product.image.path, width=IMG_WIDTH, height=IMG_HEIGHT)
                img_cell.append(img)
            except:
                img_cell.append(Spacer(1, 1))
        
        # Colonne description (droite)
        desc_cell = [
            Paragraph(f"<b>{product.name}</b> - <i>{product.category.name}</i>", 
                     ParagraphStyle(
                         'ProductTitle',
                         fontSize=12,
                         leading=16,
                         textColor=colors.HexColor('#3a0ca3'),
                         spaceAfter=12
                     )),
            Paragraph(f"<b>Description:</b><br/>{product.description}", 
                     ParagraphStyle(
                         'ProductDesc',
                         fontSize=11,
                         leading=14,
                         textColor=colors.HexColor('#4a4e69'),
                         spaceAfter=12
                     ))
        ]
        
        # Ajout des deux colonnes au tableau
        product_table_data.append([img_cell, desc_cell])
        
        # Création du tableau avec espacement régulier
        product_table = Table(product_table_data, colWidths=[IMG_WIDTH, doc.width-IMG_WIDTH-48])
        product_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (1,0), (1,0), 12),
            ('RIGHTPADDING', (0,0), (0,0), 12),
            ('BOTTOMPADDING', (0,0), (-1,-1), 12),
        ]))
        
        elements.append(product_table)
        elements.append(HRFlowable(width="100%", thickness=0.5, 
                                 color=colors.HexColor("#e5e5e5"), spaceAfter=24))
    
    # Pied de page aligné
    footer_content = []
    
    # Section Contact
    footer_content.append(Paragraph("<b>CONTACT</b>", 
                                  ParagraphStyle(
                                      'FooterTitle',
                                      fontSize=14,
                                      leading=18,
                                      alignment=0,
                                      spaceAfter=12,
                                      textColor=colors.HexColor('#2b2d42')
                                  )))
    
    # Tableau d'informations de contact
    contact_info = [
        ["Téléphone:", profile.telephone or "Non renseigné"],
        ["Email:", request.user.email],
        ["Adresse:", f"{profile.adresse or ''}<br/>{profile.ville or ''} {profile.pays.name if profile.pays else ''}".strip()],
    ]
    
    contact_table = Table(contact_info, colWidths=[1.2*inch, 4*inch])
    contact_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('FONTSIZE', (0,0), (-1,-1), 11),
        ('LEFTPADDING', (0,0), (0,-1), 0),
        ('RIGHTPADDING', (1,0), (1,-1), 0),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    footer_content.append(contact_table)
    footer_content.append(Spacer(1, 24))
    
    # QR Code centré
    qr_data = profile.share_link or f"https://votresite.com/{request.user.username}/"
    qr_img = qrcode.make(qr_data)
    qr_buffer = BytesIO()
    qr_img.save(qr_buffer, format="PNG")
    qr_buffer.seek(0)
    
    qr_table = Table([
        [Image(qr_buffer, width=1.5*inch, height=1.5*inch)],
        [Paragraph("Scannez pour visiter mon portfolio", 
                 ParagraphStyle(
                     'QRText',
                     fontSize=10,
                     leading=12,
                     alignment=1,
                     textColor=colors.HexColor('#6c757d')
                 ))]
    ], colWidths=[2*inch])
    
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    
    footer_content.append(qr_table)
    elements.extend(footer_content)
    
    # Génération du PDF
    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()
    qr_buffer.close()
    
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="portfolio_{request.user.username}.pdf"'
    return response