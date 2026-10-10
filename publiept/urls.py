"""Routes de PubliEPT."""
from django.urls import path

from . import views

urlpatterns = [
                                             
     path("", views.accueil, name="accueil"),
     path("catalogue/", views.catalogue, name="catalogue"),
     path("publications/<int:pk>/", views.publication_detail, name="publication_detail"),
     path("specialites/", views.specialites, name="specialites"),
     path("specialites/<int:pk>/", views.specialite_detail, name="specialite_detail"),
     path("enseignants/", views.annuaire, name="annuaire"),
     path("enseignants/<int:pk>/", views.profil_enseignant, name="profil_enseignant"),

                      
     path("connexion/", views.connexion, name="connexion"),
     path("inscription/", views.inscription, name="inscription"),
     path("connexion/demo/<int:pk>/", views.connexion_demo, name="connexion_demo"),
     path("deconnexion/", views.deconnexion, name="deconnexion"),

             
    path("export/bibtex/", views.export_bibtex, name="export_bibtex"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("export/publication/<int:pk>.bib", views.export_publication_bibtex,
         name="export_publication_bibtex"),
    path("export/enseignant/<int:pk>.bib", views.export_enseignant_bibtex,
         name="export_enseignant_bibtex"),

                          
    path("enseignant/tableau-de-bord/", views.enseignant_dashboard,
         name="enseignant_dashboard"),
    path("enseignant/mes-publications/", views.mes_publications, name="mes_publications"),
    path("enseignant/nouvelle-publication/", views.publication_formulaire,
         name="publication_nouvelle"),
    path("enseignant/modifier-publication/<int:pk>/", views.publication_formulaire,
         name="publication_modifier"),
    path("enseignant/supprimer-publication/<int:pk>/", views.publication_supprimer,
         name="publication_supprimer"),
    path("enseignant/profil/", views.mon_profil, name="mon_profil"),

                                                                           
     path("api/verifier-doi/", views.api_verifier_doi, name="api_verifier_doi"),

                              
    path("administration/", views.admin_dashboard, name="admin_dashboard"),
    path("administration/publications/", views.admin_publications, name="admin_publications"),
    path("administration/publications/fusionner/", views.admin_fusionner_publications,
         name="admin_fusionner_publications"),
    path("administration/referentiels/", views.admin_referentiels, name="admin_referentiels"),
    path("administration/enseignants/", views.admin_enseignants, name="admin_enseignants"),
    path("administration/utilisateurs/", views.admin_utilisateurs, name="admin_utilisateurs"),
    path("administration/utilisateurs/<int:pk>/basculer/", views.admin_basculer_compte,
         name="admin_basculer_compte"),
    path("administration/import-export/", views.admin_import_export,
         name="admin_import_export"),
    path("administration/journal/", views.admin_journal, name="admin_journal"),
    path("administration/parametres/", views.admin_parametres, name="admin_parametres"),
]
