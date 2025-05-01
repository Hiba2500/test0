from django.db import IntegrityError
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group

from .scraper import MitulaScraper
from .forms import ProfileForm, ReclamationForm, SignUpForm, AnnonceForm, AnnonceFilterForm
from .models import Annonce, Postulation, Notification, Reclamation
from django.contrib.auth  import get_user_model
from django.contrib.auth.forms import UserChangeForm
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm



User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            role = form.cleaned_data['user_type']
            grp_name = {
                'admin': 'Admin',
                'proprietaire': 'Propriétaire',
                'locataire': 'Locataire',
            }[role]
            grp, _ = Group.objects.get_or_create(name=grp_name)
            user.groups.add(grp)
            if role == 'admin':
                user.is_staff = True
                user.save()
            login(request, user)
            return redirect('rental:home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.groups.filter(name='Locataire').exists():
                return redirect('rental:home')
            return redirect('rental:home')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('rental:home')
def about_view(request):
    return render(request, 'about.html')
def home(request):
   
    form = AnnonceFilterForm(request.GET or None)
    qs = Annonce.objects.filter(is_available=True)
    
    if form.is_valid():
        c = form.cleaned_data
        if c['titre']:
            qs = qs.filter(titre__icontains=c['titre'])
        if c['ville']:
            qs = qs.filter(ville__icontains=c['ville'])
        if c['surface_min'] is not None:
            qs = qs.filter(surface__gte=c['surface_min'])
        if c['surface_max'] is not None:
            qs = qs.filter(surface__lte=c['surface_max'])
        if c['prix_min'] is not None:
            qs = qs.filter(prix__gte=c['prix_min'])
        if c['prix_max'] is not None:
            qs = qs.filter(prix__lte=c['prix_max'])
        if c['secteur']:
            qs = qs.filter(secteur__icontains=c['secteur'])
        if c['type_bien']:
            qs = qs.filter(type_bien=c['type_bien'])
        if c['chambres'] is not None:
            qs = qs.filter(chambres__gte=c['chambres'])
        if c['salles_bain'] is not None:
            qs = qs.filter(salles_bain__gte=c['salles_bain'])

    # Attacher l'image principale ou un placeholder
    annonces = []
    for annonce in qs:
        annonce.main_image = annonce.image_principale or '/static/images/placeholder.png'
        annonces.append(annonce)
    city_names = [
       
         "Ben Guerir"
    ]
    annonces_externes_by_city = {}
    
    
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
    else:
        unread_count = 0

    for city in city_names:
        slug = city.lower().replace(' ', '-')
        try:
            scraper = MitulaScraper(city=slug, pages=1)
            annonces_externes_by_city[city] = scraper.scrape()
        except Exception:
            annonces_externes_by_city[city] = []

    

    return render(request, 'home.html', {
        'filter_form': form,
        'annonces': qs,
        'annonces_externes_by_city': annonces_externes_by_city,
        'unread_count': unread_count,
    })
@login_required
def annonce_detail(request, annonce_id):
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    is_locataire = request.user.groups.filter(name='Locataire').exists()
    unread = Notification.objects.filter(recipient=request.user, is_read=False).count()

    # 1) Préparer la liste des images
    images = []
    if annonce.image_principale:
        images.append(annonce.image_principale)
    if annonce.autres_images:
        images.extend(annonce.autres_images)

    # 2) Préparer la liste des équipements actifs
    equip_map = {
        'Ascenseur':        annonce.ascenseur,
        'Balcon':           annonce.balcon,
        'Chauffage':        annonce.chauffage,
        'Climatisation':    annonce.climatisation,
        'Cuisine équipée':  annonce.cuisine_equipee,
        'Meublé':           annonce.meuble,
        'Parking':          annonce.parking,
        'Sécurité':         annonce.securite,
        'Terrasse':         annonce.terrasse,
        'Piscine':          annonce.piscine,
    }
    equipment_list = [name for name, active in equip_map.items() if active]

    return render(request, 'annonce_detail.html', {
        'annonce':        annonce,
        'images':         images,
        'equipment_list': equipment_list,
        'is_locataire':   is_locataire,
        'unread_count':   unread,
    })

@login_required
def create_annonce(request):
    if not request.user.groups.filter(name='Propriétaire').exists():
        return render(request, 'access_denied.html')

    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES)
        if form.is_valid():
            annonce = form.save(commit=False)
            annonce.proprietaire = request.user
            annonce.save()
            return redirect('rental:annonces_list')
    else:
        form = AnnonceForm()

    return render(request, 'create_annonce.html', {'form': form})

@login_required
def annonces_list(request):
    user = request.user
    if user.groups.filter(name='Locataire').exists():
        qs = Annonce.objects.filter(is_available=True)
    elif user.groups.filter(name='Propriétaire').exists():
        qs = Annonce.objects.filter(proprietaire=user)
    else:
        return render(request, 'access_denied.html')

    # Préparer une liste d'images pour chaque annonce
    annonces_with_images = []
    for annonce in qs:
        images = []
        # 1) image principale
        if annonce.image_principale:
            images.append(annonce.image_principale)
        # 2) autres images stockées en JSONField (liste de URLs)
        if annonce.autres_images:
            images.extend(annonce.autres_images)
        # On attache dynamiquement cet attribut à l’objet
        annonce.images = images
        annonces_with_images.append(annonce)

    return render(request, 'annonces_list.html', {
        'annonces': annonces_with_images
    })

@login_required
def postuler_annonce(request, annonce_id):
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    if request.method == 'POST':
        nom       = request.POST.get('nom', '').strip()
        prenom    = request.POST.get('prenom', '').strip()
        email     = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        message   = request.POST.get('message', '').strip()

        if not all([nom, prenom, email, telephone, message]):
            return render(request, 'postuler.html', {
                'annonce': annonce,
                'error': "Tous les champs sont obligatoires."
            })

        if Postulation.objects.filter(annonce=annonce, locataire=request.user).exists():
            return render(request, 'postuler.html', {
                'annonce': annonce,
                'error': "Vous avez déjà postulé à cette annonce."
            })

        try:
            post = Postulation.objects.create(
                annonce=annonce,
                locataire=request.user,
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                message=message,
                status="PENDING"
            )
            Notification.objects.create(
                recipient=annonce.proprietaire,
                postulation=post,
                message=f"{request.user.username} a postulé à votre annonce «{annonce.titre}».",
            )
        except IntegrityError:
            return render(request, 'postuler.html', {
                'annonce': annonce,
                'error': "Une erreur est survenue : vous avez peut‑être déjà postulé."
            })

        return redirect('rental:annonce_detail', annonce_id=annonce.pk)

    return render(request, 'postuler.html', {'annonce': annonce})

@login_required
def notifications_list(request):
    notes = Notification.objects.filter(recipient=request.user).order_by('-created')
    return render(request, 'notifications.html', {'notifications': notes})

@login_required
def notifications_details(request, pk):
    """
    Détail d’une notification (identifiée par 'pk').
    """
    note = get_object_or_404(Notification, pk=pk, recipient=request.user)

    if not note.is_read:
        note.is_read = True
        note.save()

    # Si c'est une notif de postulation, on récupère l’objet Postulation
    if not hasattr(note, 'postulation'):
        return redirect('rental:notifications_list')

    postu    = note.postulation
    is_owner = request.user == postu.annonce.proprietaire

    # Traitement POST (accept/refuse)
    if is_owner and request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accepted':
            postu.status = 'ACCEPTED'
        elif action == 'refused':
            postu.status = 'REFUSED'
        else:
            return HttpResponseForbidden()
        postu.save()

        Notification.objects.create(
            recipient=postu.locataire,
            postulation=postu,
            message=f"Votre candidature pour « {postu.annonce.titre} » a été {postu.get_status_display()}.",
        )
        return redirect('rental:notifications_details', pk=pk)

    return render(request, 'notifications_details.html', {
        'postulation': postu,
        'is_owner':    is_owner,
    })


@login_required
def repondre_postulation(request, postulation_id, action):
    postu = get_object_or_404(Postulation, pk=postulation_id)
    if request.user != postu.annonce.proprietaire:
        return HttpResponseForbidden()

    if action == 'accepted':
        postu.status = Postulation.ACCEPTED
    elif action == 'refused':
        postu.status = Postulation.REFUSED
    postu.save()

    Notification.objects.create(
        recipient=postu.locataire,
        postulation=postu,
        message=f"Votre demande pour «{postu.annonce.titre}» a été {postu.get_status_display()}.",
    )

    return redirect('rental:notifications')
@login_required
def profile(request):
    return render(request, 'registration/profile.html')

@login_required
def profile_edit(request):
    # Instancier les deux formulaires
    profile_form = ProfileForm(request.POST or None, instance=request.user)
    pwd_form     = PasswordChangeForm(user=request.user, data=request.POST or None)

    if request.method == 'POST':
        # Quel bouton a été cliqué ?
        if 'submit_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, "Vos informations ont été mises à jour.")
            return redirect('rental:profile_edit')

        if 'submit_password' in request.POST and pwd_form.is_valid():
            user = pwd_form.save()
            update_session_auth_hash(request, user)  # Garde l'utilisateur connecté
            messages.success(request, "Votre mot de passe a été changé.")
            return redirect('rental:profile_edit')

    return render(request, 'registration/profile_edit.html', {
        'profile_form': profile_form,
        'pwd_form':     pwd_form,
    })


from .models import Reclamation

def mes_reclamations(request):
    reclamations = Reclamation.objects.filter(utilisateur=request.user).order_by('-date_creation')
    return render(request, 'mes_reclamations.html', {'reclamations': reclamations})


def creer_reclamation(request):
    if request.method == 'POST':
        form = ReclamationForm(request.POST, user=request.user)
        if form.is_valid():
            reclamation = form.save(commit=False)
            reclamation.utilisateur = request.user
            if form.cleaned_data.get('titre_annonce'):
                reclamation.annonce = form.cleaned_data['titre_annonce']
            reclamation.save()
            return redirect('rental:mes_reclamations')
    else:
        form = ReclamationForm(user=request.user)
    return render(request, 'creer_reclamation.html', {'form': form})

@login_required
def detail_reclamation(request, id):
    reclamation = Reclamation.objects.get(id=id, utilisateur=request.user)
    return render(request, 'detail_reclamation.html', {'reclamation': reclamation})

def admin_reclamations(request):
    reclamations = Reclamation.objects.all()
    return render(request, 'reclamations/admin_reclamations.html', {'reclamations': reclamations})

def update_reclamation(request, id):
    reclamation = get_object_or_404(Reclamation, id=id)
    if request.method == 'POST':
        reclamation.statut = request.POST.get('statut')
        reclamation.reponse_admin = request.POST.get('reponse')
        reclamation.save()
        return redirect('admin_reclamations')
    return render(request, 'reclamations/update_reclamation.html', {'reclamation': reclamation})
    
@login_required
def edit_annonce(request, annonce_id):
    """Vue pour permettre au propriétaire de modifier son annonce."""
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de cette annonce
    if request.user != annonce.proprietaire:
        return render(request, 'access_denied.html')
    
    if request.method == 'POST':
        form = AnnonceForm(request.POST, request.FILES, instance=annonce)
        if form.is_valid():
            form.save()
            messages.success(request, "L'annonce a été modifiée avec succès.")
            return redirect('rental:annonce_detail', annonce_id=annonce.pk)
    else:
        form = AnnonceForm(instance=annonce)
    
    return render(request, 'edit_annonce.html', {'form': form, 'annonce': annonce})

@login_required
def delete_annonce(request, annonce_id):
    """Vue pour permettre au propriétaire de supprimer son annonce."""
    annonce = get_object_or_404(Annonce, pk=annonce_id)
    
    # Vérifier que l'utilisateur est bien le propriétaire de cette annonce
    if request.user != annonce.proprietaire:
        return render(request, 'access_denied.html')
    
    if request.method == 'POST':
        # Supprimer l'annonce et rediriger vers la liste des annonces
        annonce_titre = annonce.titre
        annonce.delete()
        messages.success(request, f"L'annonce '{annonce_titre}' a été supprimée avec succès.")
        return redirect('rental:annonces_list')
    
    # Si la méthode est GET, afficher la page de confirmation
    return render(request, 'delete_annonce.html', {'annonce': annonce})