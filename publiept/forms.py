"""Formulaires de PubliEPT."""
from django import forms

from .models import (
    DOMAINE_INSTITUTIONNEL,
    GRADES,
    Enseignant,
    est_adresse_institutionnelle,
    Financement,
    MotCle,
    ParametresEtablissement,
    Publication,
    RoleUtilisateur,
    Specialite,
    Support,
    Utilisateur,
)

CLASSE_CHAMP = (
    "w-full p-2.5 text-xs bg-slate-50 border border-slate-300 rounded-xl "
    "focus:bg-white focus:outline-none focus:ring-2 focus:ring-blue-900/20 text-slate-900"
)
CLASSE_ZONE = CLASSE_CHAMP + " leading-relaxed"


def _styler(champs, classe=CLASSE_CHAMP):
    for champ in champs.values():
        if isinstance(champ.widget, forms.CheckboxInput):
            champ.widget.attrs.setdefault("class", "w-4 h-4 text-blue-900 rounded")
        elif isinstance(champ.widget, forms.Textarea):
            champ.widget.attrs.setdefault("class", CLASSE_ZONE)
            champ.widget.attrs.setdefault("rows", 4)
        else:
            champ.widget.attrs.setdefault("class", classe)


class PublicationForm(forms.ModelForm):
    """Formulaire de dépôt / modification d'une publication."""

    mots_cles_texte = forms.CharField(
        label="Mots-clés", required=False,
        help_text="Séparés par des virgules.",
        widget=forms.TextInput(attrs={"placeholder": "Ex. Traitement du signal, Ontologies, Cryptographie"}),
    )
    organismes = forms.ModelMultipleChoiceField(
        label="Organismes co-financeurs",
        queryset=Financement.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
    )

    class Meta:
        model = Publication
        fields = [
            "titre", "type_publication", "specialite", "support", "annee",
            "volume", "numero", "pages", "doi", "lien", "resume",
            "est_financee", "pdf_nom", "pdf_taille",
        ]
        widgets = {
            "resume": forms.Textarea(attrs={"rows": 5}),
            "titre": forms.TextInput(attrs={
                "placeholder": "Titre complet de la publication, tel qu'il est publié…"
            }),
            "doi": forms.TextInput(attrs={
                "placeholder": "Ex. 10.1109/TSG.2024.3389012",
                "class": CLASSE_CHAMP + " font-mono",
            }),
            "lien": forms.URLInput(attrs={"placeholder": "https://…"}),
            "volume": forms.TextInput(attrs={"placeholder": "Ex. 15"}),
            "numero": forms.TextInput(attrs={"placeholder": "Ex. 4"}),
            "pages": forms.TextInput(attrs={"placeholder": "Ex. 120-135"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["support"].required = False
        self.fields["support"].empty_label = "Sélectionner un support du référentiel…"
        self.fields["doi"].required = False
        _styler(self.fields)
        if self.instance.pk:
            self.fields["mots_cles_texte"].initial = ", ".join(
                m.libelle for m in self.instance.mots_cles.all()
            )
            self.fields["organismes"].initial = self.instance.financements.all()

    def clean_doi(self):
        doi = (self.cleaned_data.get("doi") or "").strip()
        if not doi:
            return None
        doublon = Publication.objects.filter(doi__iexact=doi)
        if self.instance.pk:
            doublon = doublon.exclude(pk=self.instance.pk)
        if doublon.exists():
            raise forms.ValidationError(
                f"Une publication portant le DOI « {doi} » existe déjà dans PubliEPT."
            )
        return doi

    def clean(self):
        donnees = super().clean()
        type_pub = donnees.get("type_publication")
                                                                                  
        if type_pub in ("PREPRINT", "COMMUNICATION"):
            donnees["support"] = None
        return donnees

    def mots_cles_nettoyes(self):
        brut = self.cleaned_data.get("mots_cles_texte") or ""
        return [m.strip() for m in brut.split(",") if m.strip()]


class EnseignantForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = [
            "prenom", "nom", "email", "grade", "specialite", "orcid",
            "google_scholar", "biographie", "telephone", "bureau", "photo",
        ]
        widgets = {
            "biographie": forms.Textarea(attrs={"rows": 4}),
            "orcid": forms.TextInput(attrs={
                "placeholder": "0000-0002-1845-9201",
                "class": CLASSE_CHAMP + " font-mono",
            }),
            "google_scholar": forms.URLInput(attrs={
                "placeholder": "https://scholar.google.com/citations?user=…"
            }),
            "telephone": forms.TextInput(attrs={"placeholder": "+221 …"}),
            "bureau": forms.TextInput(attrs={"placeholder": "Bâtiment A, Bureau 104"}),
            "photo": forms.URLInput(attrs={"placeholder": "https://…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styler(self.fields)


class UtilisateurForm(forms.ModelForm):
    fiche_enseignant = forms.ModelChoiceField(
        label="Lier à la fiche enseignant EPT",
        queryset=Enseignant.objects.all(), required=False,
        empty_label="Aucune fiche liée",
    )

    class Meta:
        model = Utilisateur
        fields = ["first_name", "last_name", "email", "role", "telephone", "avatar"]
        labels = {"first_name": "Prénom", "last_name": "Nom"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = [
            (RoleUtilisateur.ENSEIGNANT, "Enseignant-Chercheur (dépôt et gestion)"),
            (RoleUtilisateur.ADMINISTRATEUR, "Administrateur (pilotage et référentiels)"),
        ]
        _styler(self.fields)
        if self.instance.pk:
            self.fields["fiche_enseignant"].initial = self.instance.fiche_enseignant


class InscriptionForm(forms.Form):
    """Création d'un compte enseignant-chercheur.

    La plateforme est réservée à l'École Polytechnique de Thiès : seule une
    adresse se terminant par « @ept.edu.sn » est acceptée.
    """

    prenom = forms.CharField(label="Prénom", max_length=120)
    nom = forms.CharField(label="Nom", max_length=120)
    email = forms.EmailField(
        label="Adresse email institutionnelle",
        help_text=f"Obligatoirement une adresse « @{DOMAINE_INSTITUTIONNEL} ».",
    )
    specialite = forms.ModelChoiceField(
        label="Spécialité de rattachement",
        queryset=Specialite.objects.all(),
        empty_label="Choisissez une spécialité",
    )
    grade = forms.ChoiceField(label="Grade académique", choices=GRADES)
    telephone = forms.CharField(label="Téléphone", max_length=40, required=False)
    mot_de_passe = forms.CharField(
        label="Mot de passe", widget=forms.PasswordInput, min_length=8,
        help_text="Huit caractères au minimum.",
    )
    confirmation = forms.CharField(
        label="Confirmation du mot de passe", widget=forms.PasswordInput,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].widget.attrs["placeholder"] = f"prenom.nom@{DOMAINE_INSTITUTIONNEL}"
        _styler(self.fields)

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if not est_adresse_institutionnelle(email):
            raise forms.ValidationError(
                "La plateforme est réservée à l'École Polytechnique de Thiès : "
                f"utilisez votre adresse « @{DOMAINE_INSTITUTIONNEL} »."
            )
        if Utilisateur.objects.filter(email__iexact=email).exists() \
                or Enseignant.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Un compte existe déjà pour cette adresse. Connectez-vous ou "
                "contactez l'administration."
            )
        return email

    def clean(self):
        donnees = super().clean()
        if donnees.get("mot_de_passe") and donnees.get("confirmation") \
                and donnees["mot_de_passe"] != donnees["confirmation"]:
            self.add_error("confirmation", "Les deux mots de passe ne correspondent pas.")
        return donnees

    def identifiant(self):
        """Identifiant de connexion : la partie gauche de l'adresse."""
        base = self.cleaned_data["email"].split("@")[0]
        identifiant, suffixe = base, 2
        while Utilisateur.objects.filter(username__iexact=identifiant).exists():
            identifiant = f"{base}{suffixe}"
            suffixe += 1
        return identifiant


class SpecialiteForm(forms.ModelForm):
    class Meta:
        model = Specialite
        fields = ["code", "libelle", "description", "couleur"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "code": forms.TextInput(attrs={"placeholder": "Ex. TSI"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styler(self.fields)

    def clean_code(self):
        return self.cleaned_data["code"].strip().upper()


class SupportForm(forms.ModelForm):
    class Meta:
        model = Support
        fields = ["nom", "type_support", "issn_isbn", "editeur", "pays",
                  "est_indexe", "facteur_impact"]
        widgets = {"issn_isbn": forms.TextInput(attrs={"class": CLASSE_CHAMP + " font-mono"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styler(self.fields)


class FinancementForm(forms.ModelForm):
    class Meta:
        model = Financement
        fields = ["organisme", "categorie", "type_financement", "reference_projet",
                  "annee_debut", "annee_fin", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "reference_projet": forms.TextInput(attrs={"class": CLASSE_CHAMP + " font-mono"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styler(self.fields)


class MotCleForm(forms.ModelForm):
    class Meta:
        model = MotCle
        fields = ["libelle"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styler(self.fields)


class ParametresForm(forms.ModelForm):
    class Meta:
        model = ParametresEtablissement
        fields = [
            "nom_etablissement", "sigle", "ville", "pays", "annee_universitaire",
            "directeur_recherche", "contact_email", "site_web", "devise",
        ]
        widgets = {
            "sigle": forms.TextInput(attrs={"class": CLASSE_CHAMP + " font-mono font-bold"}),
            "annee_universitaire": forms.TextInput(attrs={"placeholder": "2025-2026"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _styler(self.fields)
