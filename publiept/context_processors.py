"""Variables mises à disposition de tous les gabarits."""
from .models import ParametresEtablissement, Publication, Specialite


def contexte_publiept(request):
    return {
        "parametres": ParametresEtablissement.charger(),
        "nb_publications_total": Publication.objects.count(),
        "specialites_menu": Specialite.objects.all(),
    }
