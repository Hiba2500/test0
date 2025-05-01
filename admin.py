# rental/admin.py
from django.contrib import admin
from .models import (
    Annonce,
    Postulation,
    Notification,
    Commentaire,
    Evaluation,
    Reclamation
)

@admin.register(Annonce)
class AnnonceAdmin(admin.ModelAdmin):
    list_display = (
        'titre', 'ville', 'surface', 'prix', 'is_available', 'date_creation', 'proprietaire'
    )
    list_filter = ('ville', 'type_bien', 'is_available')
    search_fields = ('titre', 'ville', 'description')
    date_hierarchy = 'date_creation'

@admin.register(Postulation)
class PostulationAdmin(admin.ModelAdmin):
    list_display = (
        'annonce', 'locataire', 'nom', 'prenom', 'email', 'telephone', 'status', 'date_postule'
    )
    list_filter = ('status',)
    search_fields = ('nom', 'prenom', 'email', 'message')
    date_hierarchy = 'date_postule'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('recipient', 'postulation', 'message', 'is_read', 'created')
    list_filter = ('is_read',)
    search_fields = ('message',)
    date_hierarchy = 'created'

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('annonce', 'auteur', 'date_creation')
    search_fields = ('texte',)
    date_hierarchy = 'date_creation'

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ('annonce', 'utilisateur', 'note', 'date_creation')
    list_filter = ('note',)
    search_fields = ('commentaire',)
    date_hierarchy = 'date_creation'

@admin.register(Reclamation)
class ReclamationAdmin(admin.ModelAdmin):
    list_display = (
        'utilisateur', 'annonce', 'type_reclamation', 'statut', 'date_creation', 'reponse_admin'
    )
    list_filter = ('type_reclamation', 'statut')
    search_fields = ('description', 'reponse_admin')
    date_hierarchy = 'date_creation'
