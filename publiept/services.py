"""
Services métier de PubliEPT : filtrage du catalogue, statistiques de
pilotage, exports bibliographiques et import CSV.
"""
import csv
import io
import re

from django.db.models import Count, Q

from .models import (
    CategorieFinancement,
    Enseignant,
    Financement,
    MotCle,
    Publication,
    Specialite,
    Support,
    TypePublication,
)


                                                                            
                          
                                                                            
def filtrer_publications(params):
    """Applique les filtres combinables du catalogue.

    `params` est un QueryDict (request.GET). Tous les filtres sont
    facultatifs et se combinent entre eux.
    """
    qs = (
        Publication.objects.select_related("specialite", "support", "deposant")
        .prefetch_related(
            "lignes_auteurs__auteur", "mots_cles", "lignes_financements__financement"
        )
    )

    recherche = (params.get("q") or "").strip()
    if recherche:
        qs = qs.filter(
            Q(titre__icontains=recherche)
            | Q(resume__icontains=recherche)
            | Q(doi__icontains=recherche)
            | Q(mots_cles__libelle__icontains=recherche)
            | Q(auteurs__nom__icontains=recherche)
            | Q(auteurs__prenom__icontains=recherche)
            | Q(auteurs__institution__icontains=recherche)
        ).distinct()

    specialite = (params.get("specialite") or "").strip()
    if specialite:
        qs = qs.filter(specialite_id=specialite)

    type_pub = (params.get("type") or "").strip()
    if type_pub:
        qs = qs.filter(type_publication=type_pub)

    finance = (params.get("finance") or "tous").strip()
    if finance == "true":
        qs = qs.filter(est_financee=True)
    elif finance == "false":
        qs = qs.filter(est_financee=False)

    annee_min = (params.get("anneeMin") or "").strip()
    if annee_min.isdigit():
        qs = qs.filter(annee__gte=int(annee_min))

    annee_max = (params.get("anneeMax") or "").strip()
    if annee_max.isdigit():
        qs = qs.filter(annee__lte=int(annee_max))

    auteur = (params.get("auteur") or "").strip()
    if auteur:
        qs = qs.filter(
            Q(auteurs__nom__icontains=auteur) | Q(auteurs__prenom__icontains=auteur)
        ).distinct()

    enseignant = (params.get("enseignant") or "").strip()
    if enseignant:
        qs = qs.filter(lignes_auteurs__auteur__enseignant_id=enseignant).distinct()

    mot_cle = (params.get("motCle") or "").strip()
    if mot_cle:
        qs = qs.filter(mots_cles__libelle__iexact=mot_cle).distinct()

    support = (params.get("support") or "").strip()
    if support:
        qs = qs.filter(support_id=support)

    categorie = (params.get("categorie") or "").strip()
    if categorie:
        qs = qs.filter(financements__categorie=categorie).distinct()

    tri = params.get("tri") or "date_desc"
    ordres = {
        "date_desc": ["-annee", "-date_depot"],
        "date_asc": ["annee", "date_depot"],
        "titre_asc": ["titre"],
        "titre_desc": ["-titre"],
        "citations": ["-citations_count"],
    }
    return qs.order_by(*ordres.get(tri, ordres["date_desc"]))


def filtres_actifs(params):
    """Indique si au moins un filtre est appliqué (pour l'affichage)."""
    cles = ["q", "specialite", "type", "anneeMin", "anneeMax", "auteur", "motCle",
            "support", "categorie"]
    if any((params.get(c) or "").strip() for c in cles):
        return True
    return (params.get("finance") or "tous") != "tous"


                                                                            
                             
                                                                            
def statistiques_globales():
    """Indicateurs du tableau de bord de l'administration."""
    publications = Publication.objects.all()
    total = publications.count()
    financees = publications.filter(est_financee=True).count()
    part_financees = round(financees / total * 100) if total else 0
    total_citations = sum(p.citations_count for p in publications)

                                                 
    annees = {}
    for pub in publications.only("annee", "est_financee"):
        entree = annees.setdefault(pub.annee, {"annee": pub.annee, "total": 0, "financees": 0})
        entree["total"] += 1
        if pub.est_financee:
            entree["financees"] += 1
    par_annee = sorted(annees.values(), key=lambda e: e["annee"])

                               
    par_specialite = [
        {
            "code": s.code,
            "libelle": s.libelle,
            "couleur": s.couleur,
            "total": s.publications.count(),
            "id": s.pk,
        }
        for s in Specialite.objects.all()
    ]
    par_specialite.sort(key=lambda e: e["total"], reverse=True)

                          
    couleurs_type = {
        "JOURNAL": "#1E3A8A",
        "CONFERENCE": "#0D9488",
        "COMMUNICATION": "#B45309",
        "PREPRINT": "#6D28D9",
    }
    par_type = [
        {
            "code": code,
            "libelle": libelle,
            "couleur": couleurs_type[code],
            "total": publications.filter(type_publication=code).count(),
        }
        for code, libelle in TypePublication.choices
    ]

                                              
    par_organisme = [
        {"organisme": f.organisme, "categorie": f.libelle_categorie,
         "total": f.publications.count()}
        for f in Financement.objects.all()
    ]
    par_organisme = [e for e in par_organisme if e["total"]]
    par_organisme.sort(key=lambda e: e["total"], reverse=True)

                                                                                        
    couleurs_categorie = {
        "MULTILATERAL": "#1E3A8A",
        "FRANCOPHONE": "#6D28D9",
        "PANAFRICAIN": "#047857",
        "BILATERAL": "#0D9488",
        "FONDATION": "#BE185D",
        "NATIONAL": "#B45309",
    }
    par_categorie = []
    for code, libelle in CategorieFinancement.choices:
        nb = Publication.objects.filter(financements__categorie=code).distinct().count()
        par_categorie.append({
            "code": code, "libelle": libelle,
            "couleur": couleurs_categorie[code], "total": nb,
        })
    par_categorie.sort(key=lambda e: e["total"], reverse=True)

                                                                    
    classement_supports = [
        {
            "nom": s.nom,
            "type": s.get_type_support_display(),
            "est_indexe": s.est_indexe,
            "total": s.publications.count(),
        }
        for s in Support.objects.all()
    ]
    classement_supports.sort(key=lambda e: e["total"], reverse=True)

                                                         
    classement_enseignants = []
    for ens in Enseignant.objects.select_related("specialite"):
        classement_enseignants.append(
            {
                "id": ens.pk,
                "nom_complet": f"{ens.grade_court} {ens.prenom} {ens.nom}".strip(),
                "grade": ens.grade,
                "specialite": ens.specialite.code,
                "total": ens.nb_publications,
            }
        )
    classement_enseignants.sort(key=lambda e: e["total"], reverse=True)

    return {
        "total_publications": total,
        "total_enseignants": Enseignant.objects.count(),
        "total_specialites": Specialite.objects.count(),
        "total_financements": Financement.objects.count(),
        "part_financees": part_financees,
        "nb_financees": financees,
        "total_citations": total_citations,
        "par_annee": par_annee,
        "par_specialite": par_specialite,
        "par_type": par_type,
        "par_organisme": par_organisme,
        "par_categorie": par_categorie,
        "classement_supports": classement_supports,
        "classement_enseignants": classement_enseignants,
    }


def detecter_doublons():
    """Publications partageant le même DOI ou un titre identique."""
    doublons = []
    vus_doi = {}
    vus_titre = {}
    for pub in Publication.objects.all():
        if pub.doi:
            vus_doi.setdefault(pub.doi.strip().lower(), []).append(pub)
        vus_titre.setdefault(pub.titre.strip().lower(), []).append(pub)
    for groupe in list(vus_doi.values()) + list(vus_titre.values()):
        if len(groupe) > 1:
            for pub in groupe:
                if pub not in doublons:
                    doublons.append(pub)
    return doublons


                                                                            
                             
                                                                            
def exporter_bibtex(publications):
    return "\n\n".join(p.citation_bibtex for p in publications)


def exporter_csv(publications):
    tampon = io.StringIO()
    writer = csv.writer(tampon, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        "ID", "Titre", "Type", "Année", "Spécialité", "Support", "Auteurs",
        "Auteur Correspondant", "DOI", "Est Financée", "Financements",
        "Mots-clés", "Citations",
    ])
    for p in publications:
        correspondant = p.auteur_correspondant
        writer.writerow([
            p.pk,
            p.titre,
            p.type_publication,
            p.annee,
            p.specialite.code if p.specialite else "",
            p.support.nom if p.support else "",
            " ; ".join(f"{a.nom_complet} ({a.institution})" for a in p.auteurs_ordonnes),
            correspondant.nom_complet if correspondant else "",
            p.doi or "",
            "OUI" if p.est_financee else "NON",
            " ; ".join(p.organismes),
            ", ".join(m.libelle for m in p.mots_cles.all()),
            p.citations_count,
        ])
    return tampon.getvalue()


def importer_csv(texte):
    """Analyse un fichier CSV d'import et retourne des dictionnaires."""
    lignes = [l for l in texte.splitlines() if l.strip()]
    if len(lignes) < 2:
        return []
    resultats = []
    for ligne in lignes[1:]:
        colonnes = [c.strip().strip('"') for c in ligne.split(";")]
        if len(colonnes) < 2:
            continue
        type_pub = colonnes[2] if len(colonnes) > 2 else "JOURNAL"
        if type_pub not in dict(TypePublication.choices):
            type_pub = "JOURNAL"
        annee = colonnes[3] if len(colonnes) > 3 else ""
        resultats.append({
            "titre": colonnes[1] or colonnes[0],
            "type_publication": type_pub,
            "annee": int(annee) if annee.isdigit() else 2026,
            "doi": colonnes[6] if len(colonnes) > 6 else "",
            "est_financee": (colonnes[7].upper() == "OUI") if len(colonnes) > 7 else False,
            "mots_cles": [m.strip() for m in colonnes[9].split(",")] if len(colonnes) > 9 and colonnes[9] else [],
        })
    return resultats
