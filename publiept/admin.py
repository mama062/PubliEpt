"""Administration Django de PubliEPT."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Auteur,
    AuteurPublication,
    Enseignant,
    Financement,
    JournalActivite,
    MotCle,
    ParametresEtablissement,
    Publication,
    PublicationFinancement,
    Specialite,
    Support,
    Utilisateur,
)


@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ("username", "first_name", "last_name", "email", "role", "is_active")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("PubliEPT", {"fields": ("role", "telephone", "avatar", "date_creation")}),
    )

    def save_model(self, request, obj, form, change):
        obj.est_actif = obj.is_active
        super().save_model(request, obj, form, change)


@admin.register(Specialite)
class SpecialiteAdmin(admin.ModelAdmin):
    list_display = ("code", "libelle", "nb_enseignants", "nb_publications")
    search_fields = ("code", "libelle")


@admin.register(Support)
class SupportAdmin(admin.ModelAdmin):
    list_display = ("nom", "type_support", "editeur", "est_indexe", "nb_publications")
    list_filter = ("type_support", "est_indexe")
    search_fields = ("nom", "editeur", "issn_isbn")


@admin.register(Financement)
class FinancementAdmin(admin.ModelAdmin):
    list_display = ("organisme", "categorie", "type_financement", "reference_projet",
                    "annee_debut", "annee_fin", "nb_publications")
    list_filter = ("categorie",)
    search_fields = ("organisme", "reference_projet")


@admin.register(MotCle)
class MotCleAdmin(admin.ModelAdmin):
    list_display = ("libelle", "nb_publications")
    search_fields = ("libelle",)


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "grade", "specialite", "email", "nb_publications")
    list_filter = ("specialite", "grade")
    search_fields = ("nom", "prenom", "email", "orcid")


@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ("nom", "prenom", "institution", "enseignant")
    list_filter = ("institution",)
    search_fields = ("nom", "prenom", "institution")


class LigneAuteurInline(admin.TabularInline):
    model = AuteurPublication
    extra = 1
    autocomplete_fields = ["auteur"]
    ordering = ["ordre"]


class LigneFinancementInline(admin.TabularInline):
    model = PublicationFinancement
    extra = 0


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("titre", "type_publication", "annee", "specialite",
                    "est_financee", "support")
    list_filter = ("type_publication", "annee", "specialite", "est_financee")
    search_fields = ("titre", "resume", "doi")
    filter_horizontal = ("mots_cles",)
    inlines = [LigneAuteurInline, LigneFinancementInline]
    date_hierarchy = "date_depot"


@admin.register(JournalActivite)
class JournalActiviteAdmin(admin.ModelAdmin):
    list_display = ("date_action", "action", "type_action", "entite", "auteur_nom")
    list_filter = ("type_action", "entite")
    search_fields = ("action", "details", "auteur_nom")


@admin.register(ParametresEtablissement)
class ParametresAdmin(admin.ModelAdmin):
    list_display = ("nom_etablissement", "sigle", "annee_universitaire")
