from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Annonce, Postulation, Reclamation

class SignUpForm(UserCreationForm):
    email      = forms.EmailField(max_length=254, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name  = forms.CharField(max_length=30, required=True)
    ROLE_CHOICES = [
       
        ('proprietaire', 'Propriétaire'),
        ('locataire', 'Locataire'),
    ]
    user_type = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect,
        label='Rôle'
    )

    class Meta:
        model  = User
        fields = [
            'username', 'first_name', 'last_name',
            'email', 'user_type', 'password1', 'password2'
        ]



class AnnonceForm(forms.ModelForm):
    class Meta:
        model = Annonce
        fields = [
            'titre', 'description', 'prix', 'adresse', 'ville', 'surface',
            'etage', 'image_principale', 'type_bien', 'chambres', 'salles_bain',
            'parking', 'terrasse', 'piscine', 'balcon', 'ascenseur',
            'securite', 'cuisine_equipee', 'url_annonce'
        ]
        widgets = {
            'titre':       forms.TextInput    (attrs={'class':'form-control', 'placeholder':'Ex. Appartement lumineux'}),
            'description': forms.Textarea     (attrs={'class':'form-control', 'rows':4,      'placeholder':'Décrivez votre bien…'}),
            'prix':        forms.NumberInput  (attrs={'class':'form-control', 'min':0}),
            'adresse':     forms.TextInput    (attrs={'class':'form-control', 'placeholder':'Rue, numéro…'}),
            'ville':       forms.TextInput    (attrs={'class':'form-control', 'placeholder':'Ex. Casablanca'}),
            'surface':     forms.NumberInput  (attrs={'class':'form-control', 'min':0}),
            'etage':       forms.NumberInput  (attrs={'class':'form-control'}),
            'chambres':    forms.NumberInput  (attrs={'class':'form-control', 'min':0}),
            'salles_bain': forms.NumberInput  (attrs={'class':'form-control', 'min':0}),
            'url_annonce': forms.URLInput     (attrs={'class':'form-control', 'placeholder':'https://…'}),
            'image_principale':forms.URLInput     (attrs={'class':'form-control', 'placeholder':'https://…'}),
            # Les champs booléens sont traités ci-dessous
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Appliquer automatiquement la classe Bootstrap aux checkbox
        for name in ['parking','terrasse','piscine','balcon','ascenseur','securite','cuisine_equipee']:
            if name in self.fields:
                self.fields[name].widget.attrs.update({'class':'form-check-input'})


class AnnonceFilterForm(forms.Form):
    # Champs existants
    titre = forms.CharField(required=False)
    ville = forms.CharField(required=False)
    surface_min = forms.IntegerField(required=False, min_value=0)
    surface_max = forms.IntegerField(required=False, min_value=0)
    prix_min = forms.IntegerField(required=False, min_value=0)
    prix_max = forms.IntegerField(required=False, min_value=0)
    etage = forms.IntegerField(required=False)  # Conserver ce champ existant
    
    # Nouveaux champs
    secteur = forms.CharField(required=False)
    TYPE_BIEN_CHOICES = [
        ('', 'Tous les types'),
        ('appartement', 'Appartement'),
        ('maison', 'Maison'),
        ('studio', 'Studio'),
        ('terrain', 'Terrain'),
        ('commerce', 'Commerce'),
    ]
    type_bien = forms.ChoiceField(choices=TYPE_BIEN_CHOICES, required=False)
    chambres = forms.IntegerField(required=False, min_value=0)
    salles_bain = forms.IntegerField(required=False, min_value=0)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validation pour s'assurer que min est inférieur à max
        surface_min = cleaned_data.get('surface_min')
        surface_max = cleaned_data.get('surface_max')
        if surface_min is not None and surface_max is not None and surface_min > surface_max:
            self.add_error('surface_max', 'La surface maximum doit être supérieure à la surface minimum')
        
        prix_min = cleaned_data.get('prix_min')
        prix_max = cleaned_data.get('prix_max')
        if prix_min is not None and prix_max is not None and prix_min > prix_max:
            self.add_error('prix_max', 'Le prix maximum doit être supérieur au prix minimum')
            
        return 
    cleaned_data=forms.IntegerField(required=False, min_value=0)

class ContactForm(forms.Form):
    nom       = forms.CharField(max_length=100)
    prenom    = forms.CharField(max_length=100)
    email     = forms.EmailField()
    telephone = forms.CharField(max_length=20)
    message   = forms.CharField(widget=forms.Textarea(attrs={'rows':4}), label='Message')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
class ReclamationForm(forms.ModelForm):
    class Meta:
        model = Reclamation
        fields = ['annonce', 'type_reclamation', 'description']

    description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Décrivez votre réclamation'}))
    def __init__(self, *args, **kwargs):
        # Extract the 'user' argument from kwargs
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Add any custom logic using `self.user` if needed
