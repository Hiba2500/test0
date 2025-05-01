from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Annonce(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    # Informations générales
    surface = models.DecimalField(max_digits=6, decimal_places=2)
    ville = models.CharField(max_length=100)
    adresse = models.CharField(max_length=255, blank=True, null=True)
    etage = models.IntegerField(blank=True, null=True)
    is_available = models.BooleanField(default=True)
    date_creation = models.DateTimeField(default=timezone.now)
    proprietaire = models.ForeignKey(User, on_delete=models.CASCADE)

    # Données scrappées
    date_publication = models.DateField(blank=True, null=True)
    url_annonce = models.URLField(blank=True, null=True)
    type_bien = models.CharField(max_length=50, blank=True, null=True)
    chambres = models.PositiveIntegerField(default=0)
    salles_bain = models.PositiveIntegerField(default=0)
    salons = models.PositiveIntegerField(default=0)

    # Équipements et options
    ascenseur = models.BooleanField(default=False)
    balcon = models.BooleanField(default=False)
    chauffage = models.BooleanField(default=False)
    climatisation = models.BooleanField(default=False)
    cuisine_equipee = models.BooleanField(default=False)
    meuble = models.BooleanField(default=False)
    parking = models.BooleanField(default=False)
    securite = models.BooleanField(default=False)
    terrasse = models.BooleanField(default=False)
    piscine = models.BooleanField(default=False)

    # Images
    image = models.ImageField(upload_to='annonces/', blank=True, null=True)
    image_principale = models.URLField(blank=True, null=True)
    autres_images = models.JSONField(blank=True, null=True)
    nombre_images = models.PositiveIntegerField(default=0)

    # Propriétaire et contact
    nom_proprietaire = models.CharField(max_length=200, blank=True, null=True)
    lien_boutique = models.URLField(blank=True, null=True)
    profil = models.URLField(blank=True, null=True)
    contact = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.titre


class Postulation(models.Model):
    STATUS_CHOICES = [
        ('PENDING',  'En attente'),
        ('ACCEPTED', 'Acceptée'),
        ('REJECTED', 'Refusée'),
    ]

    annonce   = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='postulations')
    locataire = models.ForeignKey(User,    on_delete=models.CASCADE, related_name='postulations')
    nom       = models.CharField(max_length=100)
    prenom    = models.CharField(max_length=100)
    email     = models.EmailField()
    telephone = models.CharField(max_length=20)
    message   = models.TextField()
    date_postule = models.DateTimeField(auto_now_add=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')

    class Meta:
        unique_together = ('annonce', 'locataire')

    def __str__(self):
        return f"Postulation de {self.nom} {self.prenom} pour {self.annonce.titre}"


class Notification(models.Model):
    recipient   = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification')
    postulation = models.ForeignKey(Postulation, on_delete=models.CASCADE)
    message     = models.TextField()
    is_read     = models.BooleanField(default=False)
    created     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notif à {self.recipient.username} – {self.message[:20]}"


class Commentaire(models.Model):
    annonce       = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='commentaires')
    auteur        = models.ForeignKey(User, on_delete=models.CASCADE)
    texte         = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.annonce.titre}"


class Evaluation(models.Model):
    annonce       = models.ForeignKey(Annonce, on_delete=models.CASCADE, related_name='evaluations')
    utilisateur   = models.ForeignKey(User, on_delete=models.CASCADE)
    note          = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    commentaire   = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('annonce', 'utilisateur')

    def __str__(self):
        return f"Évaluation de {self.utilisateur.username}: {self.note}/5"


class Reclamation(models.Model):
    TYPE_RECLAMATION_CHOICES = [
        ('TECHNICAL', 'Technique'),
        ('ANNOUNCE',  'Sur annonce'),
    ]
    STATUT_CHOICES = [
        ('PENDING',     'En attente'),
        ('IN_PROGRESS', 'En cours'),
        ('RESOLVED',    'Résolue'),
        ('REJECTED',    'Rejetée'),
    ]

    utilisateur    = models.ForeignKey(User, on_delete=models.CASCADE)
    annonce        = models.ForeignKey(Annonce, on_delete=models.SET_NULL, null=True, blank=True)
    description    = models.TextField()
    type_reclamation = models.CharField(max_length=10, choices=TYPE_RECLAMATION_CHOICES, default='ANNOUNCE')
    statut         = models.CharField(max_length=50, choices=STATUT_CHOICES, default='PENDING')
    date_creation  = models.DateTimeField(auto_now_add=True)
    reponse_admin  = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Réclamation #{self.id} – {self.get_type_reclamation_display()}"
