from django.urls import include, path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'rental'

urlpatterns = [
    path('',                                        views.home,                   name='home'),
    path('signup/',                                 views.signup,                 name='signup'),
    path('login/',                                  views.login_view,             name='login'),
    path('logout/',                                 views.logout_view,            name='logout'),
    path('about/', views.about_view, name='about'),

    path('create/',                                 views.create_annonce,         name='create_annonce'),
    path('annonces/',                               views.annonces_list,          name='annonces_list'),
    path('annonce/<int:annonce_id>/',               views.annonce_detail,         name='annonce_detail'),
    path('annonce/<int:annonce_id>/postuler/',      views.postuler_annonce,       name='postuler_annonce'),
    path("notifications/",                  views.notifications_list,    name="notifications"),
    path(
        'notifications/<int:pk>/',
        views.notifications_details,
        name='notifications_details'
    ),
    path("postulation/<int:post_id>/<str:action>/",
         views.repondre_postulation,       name="repondre_postulation"),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    # pour le changement de mot de passe :
    path('', include('django.contrib.auth.urls')),
    path('mes-reclamations/', views.mes_reclamations, name='mes_reclamations'),
    path('creer-reclamation/', views.creer_reclamation, name='creer_reclamation'),
    path('creer-reclamation/<int:annonce_id>/', views.creer_reclamation, name='creer_reclamation_annonce'),
    path('reclamation/<int:reclamation_id>/', views.detail_reclamation, name='detail_reclamation'),
 path('annonce/<int:annonce_id>/edit/', views.edit_annonce, name='edit_annonce'),
    path('annonce/<int:annonce_id>/delete/', views.delete_annonce, name='delete_annonce'),
    
]
