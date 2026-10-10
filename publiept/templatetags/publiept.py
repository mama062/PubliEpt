"""Filtres et balises de gabarit propres à PubliEPT."""
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def url_avec(context, **kwargs):
    """Reconstruit la querystring courante en remplaçant certains paramètres.

    Sert à conserver les filtres actifs lors d'un changement de page ou de tri.
    """
    params = context["request"].GET.copy()
    for cle, valeur in kwargs.items():
        if valeur in (None, ""):
            params.pop(cle, None)
        else:
            params[cle] = valeur
    params.pop("page", None) if "page" not in kwargs else None
    encode = params.urlencode()
    return f"?{encode}" if encode else "?"


@register.filter
def get(dictionnaire, cle):
    """Accès à une clé de dictionnaire depuis un gabarit."""
    try:
        return dictionnaire.get(cle, "")
    except AttributeError:
        return ""


@register.filter
def pourcentage(partie, total):
    try:
        return round(float(partie) / float(total) * 100)
    except (ValueError, ZeroDivisionError, TypeError):
        return 0


@register.filter
def barre(valeur, maximum):
    """Largeur en pourcentage d'une barre de progression."""
    try:
        if not maximum:
            return 0
        return max(3, min(100, round(float(valeur) / float(maximum) * 100)))
    except (ValueError, TypeError):
        return 0


@register.filter
def pluriel(nombre, formes="s"):
    """`pluriel:"x"` ajoute « x » si le nombre dépasse 1."""
    try:
        return formes if int(nombre) > 1 else ""
    except (ValueError, TypeError):
        return ""


@register.simple_tag
def icone(nom, classe="w-4 h-4"):
    """Insère une icône Lucide."""
    return mark_safe(f'<i data-lucide="{nom}" class="{classe}"></i>')
