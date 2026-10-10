"""Vues de PubliEPT centralisees dans un seul module Django standard."""
import json
from functools import wraps

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from . import services
from .forms import (
    EnseignantForm,
    FinancementForm,
    InscriptionForm,
    MotCleForm,
    ParametresForm,
    PublicationForm,
    SpecialiteForm,
    SupportForm,
)
from .models import (
    Auteur,
    AuteurPublication,
    CategorieFinancement,
    DOMAINE_INSTITUTIONNEL,
    Enseignant,
    Financement,
    JournalActivite,
    MotCle,
    ParametresEtablissement,
    Publication,
    PublicationFinancement,
    RoleUtilisateur,
    Specialite,
    Support,
    TypePublication,
    Utilisateur,
)

MOT_DE_PASSE_DEMO = "publiept2026"


def role_requis(*roles):
    """Restreint une vue a certains roles, avec une page 403 explicite."""

    def decorateur(vue):
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('connexion')}?suivant={request.path}")
            if request.user.role not in roles and not request.user.is_superuser:
                return render(request, "acces_refuse.html", {"roles_requis": roles}, status=403)
            return vue(request, *args, **kwargs)

        return enveloppe

    return decorateur


def _enseignant_courant(request):
    """Fiche enseignant associee au compte connecte."""
    fiche = getattr(request.user, "enseignant", None)
    if fiche is None and request.user.is_superuser:
        fiche = Enseignant.objects.first()
    return fiche


def accueil(request):
    stats = services.statistiques_globales()
    dernieres = (
        Publication.objects.select_related("specialite", "support")
        .prefetch_related("lignes_auteurs__auteur", "lignes_financements__financement")
        .order_by("-date_depot")[:6]
    )
    contexte = {
        "stats": stats,
        "publications": dernieres,
        "specialites": Specialite.objects.all(),
        "titre_page": "Accueil",
    }
    return render(request, "public/accueil.html", contexte)


def catalogue(request):
    publications = services.filtrer_publications(request.GET)
    total = publications.count()

    paginator = Paginator(publications, 9)
    page = paginator.get_page(request.GET.get("page"))

                                                      
    parametres = request.GET.copy()
    parametres.pop("page", None)

    contexte = {
        "page_obj": page,
        "publications": page.object_list,
        "total_resultats": total,
        "specialites": Specialite.objects.all(),
        "types_publication": TypePublication.choices,
        "financements": Financement.objects.all(),
        "categories_financement": CategorieFinancement.choices,
        "filtres_actifs": services.filtres_actifs(request.GET),
        "querystring": parametres.urlencode(),
        "f": request.GET,
        "vue": request.GET.get("vue", "grille"),
        "titre_page": "Catalogue scientifique",
    }
    return render(request, "public/catalogue.html", contexte)


def publication_detail(request, pk):
    publication = get_object_or_404(
        Publication.objects.select_related("specialite", "support", "deposant")
        .prefetch_related(
            "lignes_auteurs__auteur__enseignant",
            "lignes_financements__financement",
            "mots_cles",
        ),
        pk=pk,
    )
    Publication.objects.filter(pk=pk).update(lectures_count=publication.lectures_count + 1)

    similaires = (
        Publication.objects.filter(specialite=publication.specialite)
        .exclude(pk=publication.pk)
        .select_related("specialite")[:3]
    )

    peut_modifier = False
    if request.user.is_authenticated:
        fiche = getattr(request.user, "enseignant", None)
        peut_modifier = (
            request.user.est_administrateur
            or request.user.is_superuser
            or (fiche is not None and publication.deposant_id == fiche.pk)
        )

    contexte = {
        "publication": publication,
        "similaires": similaires,
        "peut_modifier": peut_modifier,
        "titre_page": publication.titre,
    }
    return render(request, "public/publication_detail.html", contexte)


def specialites(request):
    contexte = {
        "specialites": Specialite.objects.prefetch_related("enseignants", "publications"),
        "titre_page": "Specialites d'ingenieurs",
    }
    return render(request, "public/specialites.html", contexte)


def specialite_detail(request, pk):
    specialite = get_object_or_404(Specialite, pk=pk)
    contexte = {
        "specialite": specialite,
        "enseignants": specialite.enseignants.all(),
        "publications": specialite.publications.select_related("support").prefetch_related(
            "lignes_auteurs__auteur", "lignes_financements__financement"
        ),
        "titre_page": specialite.libelle,
    }
    return render(request, "public/specialite_detail.html", contexte)


def annuaire(request):
    enseignants = Enseignant.objects.select_related("specialite")

    recherche = (request.GET.get("q") or "").strip()
    if recherche:
        from django.db.models import Q

        enseignants = enseignants.filter(
            Q(nom__icontains=recherche)
            | Q(prenom__icontains=recherche)
            | Q(grade__icontains=recherche)
            | Q(biographie__icontains=recherche)
        )

    specialite = (request.GET.get("specialite") or "").strip()
    if specialite:
        enseignants = enseignants.filter(specialite_id=specialite)

    grade = (request.GET.get("grade") or "").strip()
    if grade:
        enseignants = enseignants.filter(grade=grade)

    contexte = {
        "enseignants": enseignants,
        "specialites": Specialite.objects.all(),
        "grades": Enseignant.objects.values_list("grade", flat=True).distinct(),
        "f": request.GET,
        "titre_page": "Annuaire des chercheurs",
    }
    return render(request, "public/annuaire.html", contexte)


def profil_enseignant(request, pk):
    enseignant = get_object_or_404(Enseignant.objects.select_related("specialite"), pk=pk)
    publications = enseignant.publications.select_related("specialite", "support").prefetch_related(
        "lignes_auteurs__auteur", "lignes_financements__financement"
    )
    contexte = {
        "enseignant": enseignant,
        "publications": publications,
        "nb_financees": publications.filter(est_financee=True).count(),
        "total_citations": sum(p.citations_count for p in publications),
        "titre_page": enseignant.nom_complet,
    }
    return render(request, "public/profil_enseignant.html", contexte)


def connexion(request):
    if request.method == "POST":
        identifiant = (request.POST.get("email") or "").strip()
        mot_de_passe = request.POST.get("password") or ""

        utilisateur = None
        compte = Utilisateur.objects.filter(email__iexact=identifiant).first() or Utilisateur.objects.filter(
            username__iexact=identifiant
        ).first()
        if compte:
            utilisateur = authenticate(request, username=compte.username, password=mot_de_passe)

        if utilisateur is None:
            messages.error(
                request,
                "Identifiants incorrects. Utilisez la connexion rapide de demonstration.",
            )
        elif not utilisateur.is_active:
            messages.error(request, "Ce compte est desactive. Contactez l'administration.")
        else:
            login(request, utilisateur)
            JournalActivite.enregistrer(
                "Connexion a la plateforme",
                "connexion",
                "Utilisateur",
                details=f"Connexion de {utilisateur.nom_complet}",
                entite_id=utilisateur.pk,
                utilisateur=utilisateur,
            )
            messages.success(request, f"Bienvenue {utilisateur.prenom} {utilisateur.nom}.")
            return redirect(_accueil_du_role(utilisateur))

    contexte = {
        "comptes_demo": Utilisateur.objects.filter(is_active=True).order_by("role")[:6],
        "mot_de_passe_demo": MOT_DE_PASSE_DEMO,
        "titre_page": "Connexion",
    }
    return render(request, "public/connexion.html", contexte)


def inscription(request):
    """Creation d'un compte, reservee aux adresses « @ept.edu.sn »."""
    if request.user.is_authenticated:
        return redirect(_accueil_du_role(request.user))

    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            donnees = form.cleaned_data
            with transaction.atomic():
                compte = Utilisateur.objects.create_user(
                    username=form.identifiant(),
                    email=donnees["email"],
                    password=donnees["mot_de_passe"],
                    first_name=donnees["prenom"],
                    last_name=donnees["nom"],
                    role=RoleUtilisateur.ENSEIGNANT,
                    telephone=donnees["telephone"],
                )
                fiche = Enseignant.objects.create(
                    utilisateur=compte,
                    nom=donnees["nom"],
                    prenom=donnees["prenom"],
                    email=donnees["email"],
                    specialite=donnees["specialite"],
                    grade=donnees["grade"],
                    telephone=donnees["telephone"],
                )
                                                                            
                parametres = ParametresEtablissement.charger()
                Auteur.objects.create(
                    nom=donnees["nom"],
                    prenom=donnees["prenom"],
                    institution=f"{parametres.nom_etablissement} ({parametres.sigle})",
                    email=donnees["email"],
                    enseignant=fiche,
                )
                JournalActivite.enregistrer(
                    "Creation d'un compte enseignant-chercheur",
                    "creation",
                    "Utilisateur",
                    details=f"Inscription de {compte.nom_complet}",
                    entite_id=compte.pk,
                    utilisateur=compte,
                )
            login(request, compte)
            messages.success(
                request,
                f"Bienvenue {donnees['prenom']} {donnees['nom']}. "
                "Votre fiche chercheur est creee : vous pouvez deposer vos publications.",
            )
            return redirect("enseignant_dashboard")
    else:
        form = InscriptionForm()

    contexte = {
        "form": form,
        "domaine": DOMAINE_INSTITUTIONNEL,
        "titre_page": "Creer un compte",
    }
    return render(request, "public/inscription.html", contexte)


def _accueil_du_role(utilisateur):
    if utilisateur.est_administrateur or utilisateur.is_superuser:
        return reverse("admin_dashboard")
    if utilisateur.est_enseignant:
        return reverse("enseignant_dashboard")
    return reverse("catalogue")


@require_POST
def connexion_demo(request, pk):
    """Connexion rapide en un clic sur un compte de demonstration."""
    compte = get_object_or_404(Utilisateur, pk=pk, is_active=True)
    utilisateur = authenticate(request, username=compte.username, password=MOT_DE_PASSE_DEMO)
    if utilisateur is None:
        messages.error(request, "Connexion de demonstration indisponible pour ce compte.")
        return redirect("connexion")
    login(request, utilisateur)
    messages.info(request, f"Profil « {utilisateur.libelle_role} » active : {utilisateur.nom_complet}.")
    return redirect(_accueil_du_role(utilisateur))


def deconnexion(request):
    logout(request)
    messages.info(request, "Vous etes desormais en mode Visiteur public.")
    return redirect("accueil")


def export_bibtex(request):
    publications = services.filtrer_publications(request.GET)
    contenu = services.exporter_bibtex(publications)
    reponse = HttpResponse(contenu, content_type="application/x-bibtex; charset=utf-8")
    reponse["Content-Disposition"] = 'attachment; filename="publiept-export.bib"'
    return reponse


def export_csv(request):
    publications = services.filtrer_publications(request.GET)
    contenu = services.exporter_csv(publications)
    reponse = HttpResponse("\ufeff" + contenu, content_type="text/csv; charset=utf-8")
    reponse["Content-Disposition"] = 'attachment; filename="publiept-export.csv"'
    return reponse


def export_publication_bibtex(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    reponse = HttpResponse(publication.citation_bibtex, content_type="application/x-bibtex; charset=utf-8")
    reponse["Content-Disposition"] = f'attachment; filename="publication-{pk}.bib"'
    return reponse


def export_enseignant_bibtex(request, pk):
    enseignant = get_object_or_404(Enseignant, pk=pk)
    contenu = services.exporter_bibtex(enseignant.publications)
    reponse = HttpResponse(contenu, content_type="application/x-bibtex; charset=utf-8")
    reponse["Content-Disposition"] = f'attachment; filename="publications-{enseignant.nom.lower()}.bib"'
    return reponse


@role_requis(RoleUtilisateur.ENSEIGNANT, RoleUtilisateur.ADMINISTRATEUR)
def enseignant_dashboard(request):
    fiche = _enseignant_courant(request)
    publications = fiche.publications if fiche else Publication.objects.none()

    par_annee = []
    for annee in range(2020, 2027):
        lot = publications.filter(annee=annee)
        par_annee.append(
            {
                "annee": annee,
                "total": lot.count(),
                "financees": lot.filter(est_financee=True).count(),
            }
        )

    total = publications.count()
    financees = publications.filter(est_financee=True).count()
    contexte = {
        "fiche": fiche,
        "publications": publications.order_by("-date_depot")[:5],
        "total": total,
        "revues": publications.filter(type_publication="JOURNAL").count(),
        "financees": financees,
        "part_financees": round(financees / total * 100) if total else 0,
        "citations": sum(p.citations_count for p in publications),
        "donnees_graphique": json.dumps(par_annee),
        "titre_page": "Mon tableau de bord",
    }
    return render(request, "enseignant/dashboard.html", contexte)


@role_requis(RoleUtilisateur.ENSEIGNANT, RoleUtilisateur.ADMINISTRATEUR)
def mes_publications(request):
    fiche = _enseignant_courant(request)
    publications = fiche.publications if fiche else Publication.objects.none()

    recherche = (request.GET.get("q") or "").strip()
    if recherche:
        from django.db.models import Q

        publications = publications.filter(
            Q(titre__icontains=recherche) | Q(resume__icontains=recherche) | Q(doi__icontains=recherche)
        )
    type_pub = (request.GET.get("type") or "").strip()
    if type_pub:
        publications = publications.filter(type_publication=type_pub)
    finance = (request.GET.get("finance") or "").strip()
    if finance == "true":
        publications = publications.filter(est_financee=True)
    elif finance == "false":
        publications = publications.filter(est_financee=False)

    contexte = {
        "fiche": fiche,
        "publications": publications.select_related("specialite", "support").prefetch_related(
            "lignes_auteurs__auteur", "lignes_financements__financement"
        ),
        "total": (fiche.nb_publications if fiche else 0),
        "types_publication": TypePublication.choices,
        "f": request.GET,
        "titre_page": "Mes publications",
    }
    return render(request, "enseignant/mes_publications.html", contexte)


@role_requis(RoleUtilisateur.ENSEIGNANT, RoleUtilisateur.ADMINISTRATEUR)
def publication_formulaire(request, pk=None):
    """Depot ou modification d'une publication, en six etapes."""
    fiche = _enseignant_courant(request)
    publication = get_object_or_404(Publication, pk=pk) if pk else None
    modification = publication is not None

    if request.method == "POST":
        form = PublicationForm(request.POST, instance=publication)
        lignes = _lire_auteurs_postes(request)

        if not lignes:
            messages.error(request, "Une publication doit comporter au moins un auteur.")
        elif form.is_valid():
            with transaction.atomic():
                pub = form.save(commit=False)
                if not modification:
                    pub.deposant = fiche
                    pub.date_depot = timezone.now()
                pub.fichier_pdf = pub.pdf_nom and f"/demo-papers/{pub.pdf_nom}" or ""
                pub.save()

                            
                pub.mots_cles.clear()
                for libelle in form.mots_cles_nettoyes():
                    mot, _ = MotCle.objects.get_or_create(libelle=libelle)
                    pub.mots_cles.add(mot)

                                   
                pub.lignes_auteurs.all().delete()
                for index, ligne in enumerate(lignes, start=1):
                    auteur = _trouver_ou_creer_auteur(ligne)
                    AuteurPublication.objects.create(
                        publication=pub,
                        auteur=auteur,
                        ordre=index,
                        est_auteur_correspondant=ligne["correspondant"],
                    )

                               
                pub.lignes_financements.all().delete()
                organismes = form.cleaned_data.get("organismes")
                if pub.est_financee and organismes:
                    for organisme in organismes:
                        PublicationFinancement.objects.create(publication=pub, financement=organisme)
                else:
                    pub.est_financee = False
                    pub.save(update_fields=["est_financee"])

                JournalActivite.enregistrer(
                    "Modification de publication" if modification else "Depot de publication",
                    "modification" if modification else "creation",
                    "Publication",
                    details=f'Publication « {pub.titre} » ({pub.get_type_publication_display()})',
                    entite_id=pub.pk,
                    utilisateur=request.user,
                )

            messages.success(
                request,
                "Publication modifiee avec succes."
                if modification
                else "Publication enregistree : elle est consultable immediatement.",
            )
            return redirect("publication_detail", pk=pub.pk)
        else:
            messages.error(request, "Le formulaire comporte des erreurs, veuillez les corriger.")
    else:
        form = PublicationForm(instance=publication)
        lignes = _lignes_existantes(publication, fiche, request.user)

    contexte = {
        "form": form,
        "publication": publication,
        "modification": modification,
        "lignes_auteurs": lignes,
        "lignes_auteurs_json": json.dumps(lignes),
        "enseignants": Enseignant.objects.select_related("specialite"),
        "supports": Support.objects.all(),
        "financements": Financement.objects.all(),
        "financements_choisis": list(publication.financements.values_list("pk", flat=True)) if publication else [],
        "titre_page": "Modifier la publication" if modification else "Deposer une publication",
    }
    return render(request, "enseignant/formulaire.html", contexte)


def _lire_auteurs_postes(request):
    """Reconstitue la liste ordonnee des auteurs envoyee par le formulaire."""
    brut = request.POST.get("auteurs_json") or "[]"
    try:
        lignes = json.loads(brut)
    except ValueError:
        return []
    nettoyees = []
    for ligne in lignes:
        nom = (ligne.get("nom") or "").strip()
        prenom = (ligne.get("prenom") or "").strip()
        if not nom:
            continue
        nettoyees.append(
            {
                "nom": nom,
                "prenom": prenom,
                "institution": (ligne.get("institution") or "Ecole Polytechnique de Thies (EPT)").strip(),
                "email": (ligne.get("email") or "").strip(),
                "enseignant_id": ligne.get("enseignant_id") or None,
                "correspondant": bool(ligne.get("correspondant")),
            }
        )
    if nettoyees and not any(l["correspondant"] for l in nettoyees):
        nettoyees[0]["correspondant"] = True
    return nettoyees


def _trouver_ou_creer_auteur(ligne):
    if ligne.get("enseignant_id"):
        enseignant = Enseignant.objects.filter(pk=ligne["enseignant_id"]).first()
        if enseignant:
            auteur = getattr(enseignant, "profil_auteur", None)
            if auteur:
                return auteur
            return Auteur.objects.create(
                nom=enseignant.nom,
                prenom=enseignant.prenom,
                institution="Ecole Polytechnique de Thies (EPT)",
                email=enseignant.email,
                enseignant=enseignant,
            )
    auteur = Auteur.objects.filter(
        nom__iexact=ligne["nom"],
        prenom__iexact=ligne["prenom"],
        institution__iexact=ligne["institution"],
    ).first()
    if auteur:
        return auteur
    return Auteur.objects.create(
        nom=ligne["nom"],
        prenom=ligne["prenom"],
        institution=ligne["institution"],
        email=ligne["email"],
    )


def _lignes_existantes(publication, fiche, utilisateur):
    if publication:
        return [
            {
                "nom": l.auteur.nom,
                "prenom": l.auteur.prenom,
                "institution": l.auteur.institution,
                "email": l.auteur.email,
                "enseignant_id": l.auteur.enseignant_id,
                "correspondant": l.est_auteur_correspondant,
            }
            for l in publication.lignes_ordonnees
        ]
    if fiche:
        return [
            {
                "nom": fiche.nom,
                "prenom": fiche.prenom,
                "institution": "Ecole Polytechnique de Thies (EPT)",
                "email": fiche.email,
                "enseignant_id": fiche.pk,
                "correspondant": True,
            }
        ]
    return [
        {
            "nom": utilisateur.last_name,
            "prenom": utilisateur.first_name,
            "institution": "Ecole Polytechnique de Thies (EPT)",
            "email": utilisateur.email,
            "enseignant_id": None,
            "correspondant": True,
        }
    ]


@role_requis(RoleUtilisateur.ENSEIGNANT, RoleUtilisateur.ADMINISTRATEUR)
@require_POST
def publication_supprimer(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    fiche = _enseignant_courant(request)
    autorise = request.user.est_administrateur or request.user.is_superuser or (
        fiche and publication.deposant_id == fiche.pk
    )
    if not autorise:
        return render(request, "acces_refuse.html", status=403)

    titre = publication.titre
    publication.delete()
    JournalActivite.enregistrer(
        "Suppression de publication",
        "suppression",
        "Publication",
        details=f"Publication supprimee : « {titre} »",
        entite_id=pk,
        utilisateur=request.user,
    )
    messages.info(request, f"Publication « {titre[:50]}... » supprimee.")
    return redirect(request.POST.get("suivant") or "mes_publications")


@role_requis(RoleUtilisateur.ENSEIGNANT, RoleUtilisateur.ADMINISTRATEUR)
def mon_profil(request):
    fiche = _enseignant_courant(request)
    if fiche is None:
        messages.error(request, "Aucune fiche enseignant n'est liee a votre compte.")
        return redirect("enseignant_dashboard")

    if request.method == "POST":
        form = EnseignantForm(request.POST, instance=fiche)
        if form.is_valid():
            form.save()
            JournalActivite.enregistrer(
                "Mise a jour du profil chercheur",
                "modification",
                "Enseignant",
                details=f"Profil de {fiche.nom_complet} mis a jour",
                entite_id=fiche.pk,
                utilisateur=request.user,
            )
            messages.success(request, "Votre profil chercheur a ete mis a jour.")
            return redirect("mon_profil")
    else:
        form = EnseignantForm(instance=fiche)

    return render(
        request,
        "enseignant/profil.html",
        {"form": form, "fiche": fiche, "titre_page": "Mon profil chercheur"},
    )


@role_requis(RoleUtilisateur.ENSEIGNANT, RoleUtilisateur.ADMINISTRATEUR)
def api_verifier_doi(request):
    doi = (request.GET.get("doi") or "").strip()
    exclure = request.GET.get("exclure")
    if not doi:
        return JsonResponse({"existe": False})
    qs = Publication.objects.filter(doi__iexact=doi)
    if exclure:
        qs = qs.exclude(pk=exclure)
    existante = qs.first()
    return JsonResponse({
        "existe": existante is not None,
        "titre": existante.titre if existante else "",
    })


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_dashboard(request):
    stats = services.statistiques_globales()
    contexte = {
        "stats": stats,
        "json_annees": json.dumps(stats["par_annee"]),
        "json_types": json.dumps(stats["par_type"]),
        "json_specialites": json.dumps(stats["par_specialite"]),
        "json_categories": json.dumps(stats["par_categorie"]),
        "categories_financement": CategorieFinancement.choices,
        "organismes_referentiel": Financement.objects.all(),
        "titre_page": "Tableau de bord statistique",
    }
    return render(request, "administration/dashboard.html", contexte)


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_publications(request):
    publications = services.filtrer_publications(request.GET)
    contexte = {
        "publications": publications,
        "total": Publication.objects.count(),
        "specialites": Specialite.objects.all(),
        "doublons": services.detecter_doublons(),
        "toutes_publications": Publication.objects.only("pk", "titre", "annee"),
        "f": request.GET,
        "titre_page": "Toutes les publications",
    }
    return render(request, "administration/publications.html", contexte)


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
@require_POST
def admin_fusionner_publications(request):
    source_id = request.POST.get("source")
    cible_id = request.POST.get("cible")
    if not source_id or not cible_id or source_id == cible_id:
        messages.error(request, "Selectionnez deux publications distinctes.")
        return redirect("admin_publications")

    source = get_object_or_404(Publication, pk=source_id)
    cible = get_object_or_404(Publication, pk=cible_id)

    with transaction.atomic():
                                                                         
        for mot in source.mots_cles.all():
            cible.mots_cles.add(mot)
        for ligne in source.lignes_financements.all():
            PublicationFinancement.objects.get_or_create(publication=cible, financement=ligne.financement)
        if source.est_financee:
            cible.est_financee = True
        if not cible.doi and source.doi:
            cible.doi = source.doi
                                                                  
        ordre = cible.lignes_auteurs.count()
        for ligne in source.lignes_ordonnees:
            if not cible.lignes_auteurs.filter(auteur=ligne.auteur).exists():
                ordre += 1
                AuteurPublication.objects.create(
                    publication=cible,
                    auteur=ligne.auteur,
                    ordre=ordre,
                    est_auteur_correspondant=False,
                )
        cible.save()
        titre_source = source.titre
        source.delete()

        JournalActivite.enregistrer(
            "Fusion de doublons",
            "fusion",
            "Publication",
            details=f'« {titre_source} » fusionnee dans « {cible.titre} »',
            entite_id=cible.pk,
            utilisateur=request.user,
        )

    messages.success(request, "Fusion des doublons realisee avec succes.")
    return redirect("admin_publications")


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_referentiels(request):
    onglet = request.GET.get("onglet", "specialites")
    formulaires = {
        "specialites": SpecialiteForm,
        "supports": SupportForm,
        "financements": FinancementForm,
        "motscles": MotCleForm,
    }
    modeles = {
        "specialites": Specialite,
        "supports": Support,
        "financements": Financement,
        "motscles": MotCle,
    }
    libelles = {
        "specialites": "specialite",
        "supports": "support",
        "financements": "organisme de financement",
        "motscles": "mot-cle",
    }

    classe_form = formulaires.get(onglet, SpecialiteForm)
    modification = None
    if request.GET.get("modifier"):
        modification = modeles[onglet].objects.filter(pk=request.GET["modifier"]).first()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "fusionner":
            return _fusionner_referentiel(request, onglet, modeles[onglet], libelles[onglet])

        cible = None
        if request.POST.get("id"):
            cible = modeles[onglet].objects.filter(pk=request.POST["id"]).first()
        form = classe_form(request.POST, instance=cible)
        if form.is_valid():
            objet = form.save()
            JournalActivite.enregistrer(
                f"{'Modification' if cible else 'Creation'} d'un referentiel",
                "modification" if cible else "creation",
                "Referentiel",
                details=f"{libelles[onglet].capitalize()} : {objet}",
                entite_id=objet.pk,
                utilisateur=request.user,
            )
            messages.success(
                request,
                f"{libelles[onglet].capitalize()} "
                f"{'mis a jour' if cible else 'cree'} avec succes.",
            )
            return redirect(f"{reverse('admin_referentiels')}?onglet={onglet}")
        messages.error(request, "Le formulaire comporte des erreurs.")
    else:
        form = classe_form(instance=modification)

    contexte = {
        "onglet": onglet,
        "form": form,
        "modification": modification,
        "libelle": libelles.get(onglet, ""),
        "specialites": Specialite.objects.all(),
        "supports": Support.objects.all(),
        "financements": Financement.objects.all(),
        "motscles": MotCle.objects.all(),
        "elements": modeles[onglet].objects.all(),
        "titre_page": "Gestion des referentiels",
    }
    return render(request, "administration/referentiels.html", contexte)


def _fusionner_referentiel(request, onglet, modele, libelle):
    source = modele.objects.filter(pk=request.POST.get("source")).first()
    cible = modele.objects.filter(pk=request.POST.get("cible")).first()
    if not source or not cible or source.pk == cible.pk:
        messages.error(request, "Selectionnez deux elements distincts pour la fusion.")
        return redirect(f"{reverse('admin_referentiels')}?onglet={onglet}")

    with transaction.atomic():
        if onglet == "specialites":
            Publication.objects.filter(specialite=source).update(specialite=cible)
            Enseignant.objects.filter(specialite=source).update(specialite=cible)
        elif onglet == "supports":
            Publication.objects.filter(support=source).update(support=cible)
        elif onglet == "financements":
            for ligne in source.lignes_publications.all():
                PublicationFinancement.objects.get_or_create(publication=ligne.publication, financement=cible)
            source.lignes_publications.all().delete()
        elif onglet == "motscles":
            for publication in source.publications.all():
                publication.mots_cles.add(cible)
                publication.mots_cles.remove(source)

        nom_source = str(source)
        source.delete()
        JournalActivite.enregistrer(
            "Fusion de referentiels",
            "fusion",
            "Referentiel",
            details=f"{libelle.capitalize()} « {nom_source} » fusionne dans « {cible} »",
            entite_id=cible.pk,
            utilisateur=request.user,
        )

    messages.success(request, "Fusion effectuee : les publications ont ete migrees.")
    return redirect(f"{reverse('admin_referentiels')}?onglet={onglet}")


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_enseignants(request):
    modification = None
    if request.GET.get("modifier"):
        modification = Enseignant.objects.filter(pk=request.GET["modifier"]).first()

    if request.method == "POST":
        cible = Enseignant.objects.filter(pk=request.POST.get("id")).first()
        form = EnseignantForm(request.POST, instance=cible)
        if form.is_valid():
            enseignant = form.save()
            JournalActivite.enregistrer(
                f"{'Modification' if cible else 'Creation'} d'une fiche enseignant",
                "modification" if cible else "creation",
                "Enseignant",
                details=f"Fiche de {enseignant.nom_complet}",
                entite_id=enseignant.pk,
                utilisateur=request.user,
            )
            messages.success(request, "Fiche enseignant enregistree.")
            return redirect("admin_enseignants")
        messages.error(request, "Le formulaire comporte des erreurs.")
    else:
        form = EnseignantForm(instance=modification)

    enseignants = Enseignant.objects.select_related("specialite")
    recherche = (request.GET.get("q") or "").strip()
    if recherche:
        from django.db.models import Q

        enseignants = enseignants.filter(
            Q(nom__icontains=recherche) | Q(prenom__icontains=recherche) | Q(grade__icontains=recherche)
        )

    contexte = {
        "enseignants": enseignants,
        "form": form,
        "modification": modification,
        "f": request.GET,
        "titre_page": "Gestion des enseignants",
    }
    return render(request, "administration/enseignants.html", contexte)


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_utilisateurs(request):
    if not request.user.is_staff:
        request.user.is_staff = True
        request.user.save(update_fields=["is_staff"])
    namespace = Utilisateur._meta.app_label
    return redirect(f"admin:{namespace}_utilisateur_changelist")


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
@require_POST
def admin_basculer_compte(request, pk):
    """Active ou desactive un compte. Un compte ne se supprime jamais."""
    utilisateur = get_object_or_404(Utilisateur, pk=pk)
    utilisateur.est_actif = not utilisateur.est_actif
    utilisateur.is_active = utilisateur.est_actif
    utilisateur.save(update_fields=["est_actif", "is_active"])
    JournalActivite.enregistrer(
        "Changement de statut d'un compte",
        "modification",
        "Utilisateur",
        details=f"Compte de {utilisateur.nom_complet} "
        f"{'active' if utilisateur.est_actif else 'desactive'}",
        entite_id=utilisateur.pk,
        utilisateur=request.user,
    )
    messages.info(
        request,
        f"Compte de {utilisateur.nom_complet} "
        f"{'active' if utilisateur.est_actif else 'desactive'}.",
    )
    return redirect("admin_utilisateurs")


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_import_export(request):
    if request.method == "POST":
        contenu = request.POST.get("contenu") or ""
        if not contenu.strip():
            messages.error(request, "Veuillez coller le contenu CSV a importer.")
        else:
            lignes = services.importer_csv(contenu)
            if not lignes:
                messages.error(request, "Aucune publication valide n'a pu etre extraite.")
            else:
                specialite = Specialite.objects.first()
                fiche = _enseignant_courant(request)
                cree = 0
                for ligne in lignes:
                    if Publication.objects.filter(titre__iexact=ligne["titre"]).exists():
                        continue
                    publication = Publication.objects.create(
                        titre=ligne["titre"],
                        resume="Publication importee en lot.",
                        type_publication=ligne["type_publication"],
                        annee=ligne["annee"],
                        doi=ligne["doi"] or None,
                        est_financee=ligne["est_financee"],
                        specialite=specialite,
                        deposant=fiche,
                    )
                    for libelle in ligne["mots_cles"]:
                        mot, _ = MotCle.objects.get_or_create(libelle=libelle)
                        publication.mots_cles.add(mot)
                    cree += 1
                JournalActivite.enregistrer(
                    "Import de publications",
                    "import",
                    "Publication",
                    details=f"{cree} publication(s) importee(s) depuis un fichier CSV",
                    utilisateur=request.user,
                )
                messages.success(request, f"{cree} publication(s) importee(s) avec succes.")
        return redirect("admin_import_export")

    return render(
        request,
        "administration/import_export.html",
        {"total": Publication.objects.count(), "titre_page": "Import et export"},
    )


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_journal(request):
    evenements = JournalActivite.objects.all()
    recherche = (request.GET.get("q") or "").strip()
    if recherche:
        from django.db.models import Q

        evenements = evenements.filter(
            Q(action__icontains=recherche)
            | Q(details__icontains=recherche)
            | Q(auteur_nom__icontains=recherche)
        )
    type_action = (request.GET.get("type") or "").strip()
    if type_action:
        evenements = evenements.filter(type_action=type_action)

    paginator = Paginator(evenements, 40)
    page = paginator.get_page(request.GET.get("page"))

    contexte = {
        "page_obj": page,
        "evenements": page.object_list,
        "total": JournalActivite.objects.count(),
        "types": JournalActivite.TYPES,
        "f": request.GET,
        "titre_page": "Journal d'activite",
    }
    return render(request, "administration/journal.html", contexte)


@role_requis(RoleUtilisateur.ADMINISTRATEUR)
def admin_parametres(request):
    parametres = ParametresEtablissement.charger()
    if request.method == "POST":
        form = ParametresForm(request.POST, instance=parametres)
        if form.is_valid():
            form.save()
            JournalActivite.enregistrer(
                "Mise a jour des parametres",
                "modification",
                "Parametres",
                details="Parametres de l'etablissement modifies",
                utilisateur=request.user,
            )
            messages.success(request, "Parametres institutionnels enregistres.")
            return redirect("admin_parametres")
    else:
        form = ParametresForm(instance=parametres)

    return render(
        request,
        "administration/parametres.html",
        {"form": form, "titre_page": "Parametres de l'etablissement"},
    )


def page_404(request, exception=None):
    return render(request, "404.html", status=404)


def page_403(request, exception=None):
    return render(request, "acces_refuse.html", status=403)