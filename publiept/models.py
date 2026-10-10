"""
Modèles de PubliEPT — plateforme de centralisation des publications
scientifiques de l'École Polytechnique de Thiès.

Traduction directe du Modèle Logique de Données (MLD) du projet.
"""
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


                                                                            
                                        
                                                                            
                                                                          
                                                      
DOMAINE_INSTITUTIONNEL = "ept.edu.sn"


def est_adresse_institutionnelle(email):
    """Vrai si l'adresse appartient au domaine de l'école."""
    return (email or "").strip().lower().endswith("@" + DOMAINE_INSTITUTIONNEL)


                                                                            
                     
                                                                            
class RoleUtilisateur(models.TextChoices):
    VISITEUR = "visiteur", "Visiteur Public"
    ENSEIGNANT = "enseignant", "Enseignant-Chercheur"
    ADMINISTRATEUR = "administrateur", "Administrateur EPT"


class TypePublication(models.TextChoices):
    JOURNAL = "JOURNAL", "Article de Revue"
    CONFERENCE = "CONFERENCE", "Conférence"
    COMMUNICATION = "COMMUNICATION", "Communication"
    PREPRINT = "PREPRINT", "Preprint"


class TypeSupport(models.TextChoices):
    JOURNAL = "JOURNAL", "Revue / Journal"
    CONFERENCE = "CONFERENCE", "Conférence"


class CategorieFinancement(models.TextChoices):
    """Catégories usuelles de sources de financement de la recherche.

    Liste communiquée par la direction de la recherche de l'EPT.
    """

    MULTILATERAL = "MULTILATERAL", "Bailleurs multilatéraux / développement"
    FRANCOPHONE = "FRANCOPHONE", "Coopération francophone"
    PANAFRICAIN = "PANAFRICAIN", "Institutions panafricaines"
    BILATERAL = "BILATERAL", "Coopération bilatérale"
    FONDATION = "FONDATION", "Fondations privées"
    NATIONAL = "NATIONAL", "Financement national"


GRADES = [
    ("Professeur Titulaire", "Professeur Titulaire"),
    ("Professeur Assimilé", "Professeur Assimilé"),
    ("Maître de Conférences Titulaire", "Maître de Conférences Titulaire"),
    ("Maître de Conférences", "Maître de Conférences"),
    ("Maître-Assistant", "Maître-Assistant"),
    ("Enseignant-Chercheur", "Enseignant-Chercheur"),
    ("Assistant", "Assistant"),
    ("Chercheur Associé", "Chercheur Associé"),
]


                                                                            
             
                                                                            
class Utilisateur(AbstractUser):
    """Un utilisateur possède un et un seul rôle : enseignant ou administrateur.

    La consultation des publications ne nécessite aucun compte ; le rôle
    « visiteur » n'existe que pour les comptes de démonstration.
    """

    email = models.EmailField("adresse email", unique=True)
    role = models.CharField(
        "rôle", max_length=20, choices=RoleUtilisateur.choices,
        default=RoleUtilisateur.ENSEIGNANT,
    )
    telephone = models.CharField("téléphone", max_length=40, blank=True)
    avatar = models.CharField(
        "photo de profil", max_length=500, blank=True,
        help_text="Adresse externe (https://…) ou fichier de la plateforme "
                  "(img/enseignants/nom.jpg).",
    )
    est_actif = models.BooleanField(
        "compte actif", default=True,
        help_text="Un compte se désactive, il ne se supprime jamais.",
    )
    date_creation = models.DateField("date de création", default=timezone.now)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

                                                                            
    @property
    def avatar_url(self):
        """Accepte indifféremment une URL externe ou un fichier de la plateforme."""
        if not self.avatar:
            return ""
        if self.avatar.startswith(("http://", "https://", "/")):
            return self.avatar
        from django.templatetags.static import static
        return static(self.avatar)

    @property
    def prenom(self):
        return self.first_name

    @property
    def nom(self):
        return self.last_name

    @property
    def nom_complet(self):
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def est_enseignant(self):
        return self.role == RoleUtilisateur.ENSEIGNANT

    @property
    def est_administrateur(self):
        return self.role == RoleUtilisateur.ADMINISTRATEUR

    @property
    def fiche_enseignant(self):
        return getattr(self, "enseignant", None)

    @property
    def libelle_role(self):
        return RoleUtilisateur(self.role).label


                                                                            
              
                                                                            
class Specialite(models.Model):
    """Axe principal de classement des publications de l'EPT."""

    code = models.CharField("code", max_length=12, unique=True)
    libelle = models.CharField("libellé", max_length=200, unique=True)
    description = models.TextField("description", blank=True)
    couleur = models.CharField("couleur", max_length=9, default="#1E3A8A")
    icone = models.CharField("icône", max_length=40, blank=True, default="compass")

    class Meta:
        verbose_name = "spécialité"
        verbose_name_plural = "spécialités"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} — {self.libelle}"

    def get_absolute_url(self):
        return reverse("specialite_detail", args=[self.pk])

    @property
    def nb_publications(self):
        return self.publications.count()

    @property
    def nb_enseignants(self):
        return self.enseignants.count()

    @property
    def nb_financees(self):
        return self.publications.filter(est_financee=True).count()


class Support(models.Model):
    """Revue ou conférence dans laquelle paraît une publication."""

    nom = models.CharField("nom du support", max_length=300, unique=True)
    type_support = models.CharField(
        "type", max_length=20, choices=TypeSupport.choices, default=TypeSupport.JOURNAL
    )
    issn_isbn = models.CharField("ISSN / ISBN", max_length=60, blank=True)
    editeur = models.CharField("éditeur", max_length=200, blank=True)
    pays = models.CharField("pays", max_length=100, blank=True)
    est_indexe = models.BooleanField("indexé Scopus / WoS", default=False)
    facteur_impact = models.FloatField("facteur d'impact", null=True, blank=True)

    class Meta:
        verbose_name = "support de publication"
        verbose_name_plural = "supports de publication"
        ordering = ["nom"]

    def __str__(self):
        return self.nom

    @property
    def nb_publications(self):
        return self.publications.count()


class Financement(models.Model):
    """Organisme finançant un ou plusieurs travaux de recherche."""

    organisme = models.CharField("organisme", max_length=250)
    categorie = models.CharField(
        "catégorie de la source", max_length=20,
        choices=CategorieFinancement.choices,
        default=CategorieFinancement.NATIONAL,
        help_text="Catégorie usuelle de bailleur, utilisée pour les statistiques.",
    )
    type_financement = models.CharField("type de subvention", max_length=200, blank=True)
    reference_projet = models.CharField("référence du projet", max_length=120, blank=True)
    annee_debut = models.PositiveIntegerField("année de début", null=True, blank=True)
    annee_fin = models.PositiveIntegerField("année de fin", null=True, blank=True)
    description = models.TextField("description", blank=True)

    class Meta:
        verbose_name = "organisme de financement"
        verbose_name_plural = "organismes de financement"
        ordering = ["categorie", "organisme"]

    def __str__(self):
        return self.organisme

    @property
    def nb_publications(self):
        return self.publications.count()

    @property
    def libelle_categorie(self):
        return CategorieFinancement(self.categorie).label

    @property
    def classe_categorie(self):
        """Classes Tailwind du badge de catégorie."""
        return {
            "MULTILATERAL": "bg-blue-50 text-blue-900 border-blue-200",
            "FRANCOPHONE": "bg-purple-50 text-purple-900 border-purple-200",
            "PANAFRICAIN": "bg-emerald-50 text-emerald-900 border-emerald-200",
            "BILATERAL": "bg-teal-50 text-teal-900 border-teal-200",
            "FONDATION": "bg-pink-50 text-pink-900 border-pink-200",
            "NATIONAL": "bg-amber-50 text-amber-900 border-amber-300",
        }.get(self.categorie, "bg-slate-100 text-slate-700 border-slate-200")


class MotCle(models.Model):
    libelle = models.CharField("libellé", max_length=150, unique=True)

    class Meta:
        verbose_name = "mot-clé"
        verbose_name_plural = "mots-clés"
        ordering = ["libelle"]

    def __str__(self):
        return self.libelle

    @property
    def nb_publications(self):
        return self.publications.count()


                                                                            
            
                                                                            
class Enseignant(models.Model):
    """Un enseignant est un utilisateur, rattaché à une et une seule spécialité."""

    utilisateur = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="enseignant", null=True, blank=True,
        verbose_name="compte utilisateur",
    )
    nom = models.CharField("nom", max_length=120)
    prenom = models.CharField("prénom", max_length=120)
    email = models.EmailField("email institutionnel", unique=True)
    specialite = models.ForeignKey(
        Specialite, on_delete=models.PROTECT, related_name="enseignants",
        verbose_name="spécialité",
    )
    grade = models.CharField("grade académique", max_length=60, choices=GRADES,
                             default="Maître-Assistant")
    orcid = models.CharField("identifiant ORCID", max_length=40, blank=True)
    google_scholar = models.URLField("profil Google Scholar", max_length=400, blank=True)
    biographie = models.TextField("biographie scientifique", blank=True)
    photo = models.CharField("photo", max_length=500, blank=True,
                             help_text="URL complète, ou chemin d'un fichier de static/img/enseignants/.")
    telephone = models.CharField("téléphone", max_length=40, blank=True)
    bureau = models.CharField("bureau / laboratoire", max_length=200, blank=True)
    citations_total = models.PositiveIntegerField("citations totales", default=0)
    h_index = models.PositiveIntegerField("indice h", default=0)

    class Meta:
        verbose_name = "enseignant-chercheur"
        verbose_name_plural = "enseignants-chercheurs"
        ordering = ["nom", "prenom"]

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_absolute_url(self):
        return reverse("profil_enseignant", args=[self.pk])

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def initiales(self):
        """Repli affiché lorsque l'enseignant n'a pas fourni de photographie.

        Aucune image d'illustration n'est inventée : on affiche les initiales.
        """
        return f"{self.prenom[:1]}{self.nom[:1]}".upper()

    @property
    def photo_url(self):
        """Accepte indifféremment une URL externe ou un fichier de la plateforme."""
        if not self.photo:
            return ""
        if self.photo.startswith(("http://", "https://", "/")):
            return self.photo
        from django.templatetags.static import static
        return static(self.photo)

    @property
    def grade_court(self):
        equivalences = {
            "Professeur Titulaire": "Pr.",
            "Professeur Assimilé": "Pr.",
            "Maître de Conférences Titulaire": "Dr.",
            "Maître de Conférences": "Dr.",
            "Maître-Assistant": "Dr.",
            "Enseignant-Chercheur": "Dr.",
            "Assistant": "M.",
            "Chercheur Associé": "Dr.",
        }
        return equivalences.get(self.grade, "")

    @property
    def publications(self):
        """Toutes les publications signées par cet enseignant, même déposées
        par un collègue."""
        return Publication.objects.filter(
            lignes_auteurs__auteur__enseignant=self
        ).distinct()

    @property
    def nb_publications(self):
        return self.publications.count()


                                                                            
        
                                                                            
class Auteur(models.Model):
    """Signataire d'une publication.

    Un auteur interne est relié à un enseignant de l'EPT ; un auteur externe
    porte le nom de son institution et n'a aucun lien vers un enseignant.
    """

    nom = models.CharField("nom", max_length=120)
    prenom = models.CharField("prénom", max_length=120)
    institution = models.CharField("institution", max_length=250,
                                   default="École Polytechnique de Thiès (EPT)")
    email = models.EmailField("email", blank=True)
    enseignant = models.OneToOneField(
        Enseignant, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="profil_auteur", verbose_name="enseignant EPT",
        help_text="Vide pour un auteur externe à l'établissement.",
    )

    class Meta:
        verbose_name = "auteur"
        verbose_name_plural = "auteurs"
        ordering = ["nom", "prenom"]

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    @property
    def nom_complet(self):
        return f"{self.prenom} {self.nom}"

    @property
    def est_interne(self):
        return self.enseignant_id is not None or "thi" in self.institution.lower() \
            or "ept" in self.institution.lower()


                                                                            
             
                                                                            
class Publication(models.Model):
    """Publication scientifique, consultable dès son dépôt (aucune validation)."""

    titre = models.CharField("titre", max_length=500)
    resume = models.TextField("résumé", blank=True)
    type_publication = models.CharField(
        "type", max_length=20, choices=TypePublication.choices,
        default=TypePublication.JOURNAL,
    )
    annee = models.PositiveIntegerField("année de parution")
    volume = models.CharField("volume", max_length=40, blank=True)
    numero = models.CharField("numéro", max_length=40, blank=True)
    pages = models.CharField("pages", max_length=60, blank=True)
    doi = models.CharField(
        "identifiant DOI", max_length=200, blank=True, null=True, unique=True,
        help_text="Unique lorsqu'il est renseigné : évite les doublons entre co-auteurs.",
    )
    lien = models.URLField("lien officiel", max_length=600, blank=True)
    fichier_pdf = models.CharField("chemin du PDF", max_length=400, blank=True)
    pdf_nom = models.CharField("nom du fichier", max_length=250, blank=True)
    pdf_taille = models.CharField("taille du fichier", max_length=30, blank=True)

    est_financee = models.BooleanField("publication financée", default=False)
    date_depot = models.DateTimeField("date de dépôt", default=timezone.now)
    date_modification = models.DateTimeField("dernière modification", auto_now=True)

                                                                              
    support = models.ForeignKey(
        Support, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="publications", verbose_name="support de parution",
    )
    specialite = models.ForeignKey(
        Specialite, on_delete=models.PROTECT, related_name="publications",
        verbose_name="spécialité",
    )
    deposant = models.ForeignKey(
        Enseignant, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="depots", verbose_name="enseignant déposant",
    )

    auteurs = models.ManyToManyField(
        Auteur, through="AuteurPublication", related_name="publications",
        verbose_name="auteurs",
    )
    financements = models.ManyToManyField(
        Financement, through="PublicationFinancement", blank=True,
        related_name="publications", verbose_name="financements",
    )
    mots_cles = models.ManyToManyField(
        MotCle, blank=True, related_name="publications", verbose_name="mots-clés",
    )

    citations_count = models.PositiveIntegerField("citations", default=0)
    lectures_count = models.PositiveIntegerField("lectures", default=0)

    class Meta:
        verbose_name = "publication"
        verbose_name_plural = "publications"
        ordering = ["-annee", "-date_depot"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("publication_detail", args=[self.pk])

    def save(self, *args, **kwargs):
                                                                                  
        if self.type_publication in (TypePublication.PREPRINT, TypePublication.COMMUNICATION):
            self.support = None
        if not self.doi:
            self.doi = None                                             
        super().save(*args, **kwargs)

                                                                           
    @property
    def lignes_ordonnees(self):
        return self.lignes_auteurs.select_related("auteur", "auteur__enseignant").order_by("ordre")

    @property
    def auteurs_ordonnes(self):
        return [ligne.auteur for ligne in self.lignes_ordonnees]

    @property
    def liste_auteurs(self):
        return ", ".join(a.nom_complet for a in self.auteurs_ordonnes)

    @property
    def auteur_correspondant(self):
        ligne = self.lignes_auteurs.filter(est_auteur_correspondant=True).first()
        return ligne.auteur if ligne else None

    @property
    def organismes(self):
        return [pf.financement.organisme for pf in
                self.lignes_financements.select_related("financement")]

    @property
    def sans_support(self):
        return self.type_publication in (TypePublication.PREPRINT, TypePublication.COMMUNICATION)

    @property
    def libelle_type(self):
        return TypePublication(self.type_publication).label

    @property
    def classe_type(self):
        """Classes Tailwind du badge de type."""
        return {
            "JOURNAL": "bg-blue-50 text-blue-900 border-blue-200",
            "CONFERENCE": "bg-teal-50 text-teal-900 border-teal-200",
            "COMMUNICATION": "bg-amber-50 text-amber-900 border-amber-300",
            "PREPRINT": "bg-purple-50 text-purple-900 border-purple-200",
        }.get(self.type_publication, "bg-slate-100 text-slate-800 border-slate-200")

    @property
    def icone_type(self):
        return {
            "JOURNAL": "file-text",
            "CONFERENCE": "globe",
            "COMMUNICATION": "award",
            "PREPRINT": "circle-help",
        }.get(self.type_publication, "file-text")

                                                                           
    @property
    def citation_apa(self):
        parts = []
        for ligne in self.lignes_ordonnees:
            initiale = f"{ligne.auteur.prenom[0]}." if ligne.auteur.prenom else ""
            etiquette = f"{ligne.auteur.nom}, {initiale}"
            if ligne.est_auteur_correspondant:
                etiquette += "*"
            parts.append(etiquette)
        citation = f"{', '.join(parts)} ({self.annee}). {self.titre}. "
        if self.support:
            citation += f"{self.support.nom}. "
        if self.volume:
            citation += f"{self.volume}"
        if self.numero:
            citation += f"({self.numero}), "
        if self.pages:
            citation += f"{self.pages}. "
        if self.doi:
            citation += f"https://doi.org/{self.doi}"
        return citation.strip()

    @property
    def citation_bibtex(self):
        entree = {
            "JOURNAL": "article",
            "CONFERENCE": "inproceedings",
        }.get(self.type_publication, "misc")
        lignes = list(self.lignes_ordonnees)
        cle = f"{lignes[0].auteur.nom if lignes else 'EPT'}{self.annee}"
        auteurs = " and ".join(f"{l.auteur.nom}, {l.auteur.prenom}" for l in lignes)
        bib = f"@{entree}{{{cle},\n"
        bib += f"  title = {{{self.titre}}},\n"
        bib += f"  author = {{{auteurs}}},\n"
        bib += f"  year = {{{self.annee}}},\n"
        if self.support:
            champ = "journal" if entree == "article" else "booktitle"
            bib += f"  {champ} = {{{self.support.nom}}},\n"
        if self.volume:
            bib += f"  volume = {{{self.volume}}},\n"
        if self.numero:
            bib += f"  number = {{{self.numero}}},\n"
        if self.pages:
            bib += f"  pages = {{{self.pages}}},\n"
        if self.doi:
            bib += f"  doi = {{{self.doi}}},\n"
        mots = list(self.mots_cles.all())
        if mots:
            bib += f"  keywords = {{{', '.join(m.libelle for m in mots)}}},\n"
        bib += "  institution = {École Polytechnique de Thiès (EPT)}\n}"
        return bib


class AuteurPublication(models.Model):
    """Association publication / auteur PORTANT L'ORDRE DE SIGNATURE.

    C'est le point technique central du modèle : la position d'un auteur
    dans la liste a une signification scientifique.
    """

    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="lignes_auteurs"
    )
    auteur = models.ForeignKey(
        Auteur, on_delete=models.CASCADE, related_name="lignes_publications"
    )
    ordre = models.PositiveIntegerField("ordre de signature", default=1)
    est_auteur_correspondant = models.BooleanField("auteur correspondant", default=False)

    class Meta:
        verbose_name = "auteur d'une publication"
        verbose_name_plural = "auteurs des publications"
        ordering = ["ordre"]
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "ordre"], name="ordre_unique_par_publication"
            ),
            models.UniqueConstraint(
                fields=["publication", "auteur"], name="auteur_unique_par_publication"
            ),
        ]

    def __str__(self):
        return f"{self.ordre}. {self.auteur}"


class PublicationFinancement(models.Model):
    """Une publication peut être cofinancée par plusieurs organismes."""

    publication = models.ForeignKey(
        Publication, on_delete=models.CASCADE, related_name="lignes_financements"
    )
    financement = models.ForeignKey(
        Financement, on_delete=models.CASCADE, related_name="lignes_publications"
    )

    class Meta:
        verbose_name = "financement d'une publication"
        verbose_name_plural = "financements des publications"
        constraints = [
            models.UniqueConstraint(
                fields=["publication", "financement"], name="financement_unique_par_publication"
            )
        ]

    def __str__(self):
        return f"{self.publication} — {self.financement}"


                                                                            
                    
                                                                            
class JournalActivite(models.Model):
    TYPES = [
        ("creation", "Création"),
        ("modification", "Modification"),
        ("suppression", "Suppression"),
        ("fusion", "Fusion"),
        ("connexion", "Connexion"),
        ("import", "Import"),
        ("export", "Export"),
    ]
    ENTITES = [
        ("Publication", "Publication"),
        ("Enseignant", "Enseignant"),
        ("Utilisateur", "Utilisateur"),
        ("Referentiel", "Référentiel"),
        ("Parametres", "Paramètres"),
    ]

    action = models.CharField("action", max_length=200)
    type_action = models.CharField("type", max_length=20, choices=TYPES)
    entite = models.CharField("entité", max_length=30, choices=ENTITES)
    entite_id = models.CharField("identifiant de l'objet", max_length=60, blank=True)
    auteur_nom = models.CharField("auteur de l'action", max_length=150)
    auteur_role = models.CharField("rôle", max_length=40, blank=True)
    details = models.TextField("détails", blank=True)
    date_action = models.DateTimeField("date", default=timezone.now)

    class Meta:
        verbose_name = "événement du journal"
        verbose_name_plural = "journal d'activité"
        ordering = ["-date_action"]

    def __str__(self):
        return f"{self.action} — {self.auteur_nom}"

    @property
    def classe_badge(self):
        return {
            "creation": "bg-emerald-100 text-emerald-900",
            "modification": "bg-blue-100 text-blue-900",
            "suppression": "bg-rose-100 text-rose-900",
            "fusion": "bg-amber-100 text-amber-900",
        }.get(self.type_action, "bg-slate-100 text-slate-700")

    @classmethod
    def enregistrer(cls, action, type_action, entite, details="", entite_id="", utilisateur=None):
        return cls.objects.create(
            action=action,
            type_action=type_action,
            entite=entite,
            entite_id=str(entite_id or ""),
            details=details,
            auteur_nom=(utilisateur.nom_complet if utilisateur and utilisateur.is_authenticated
                        else "Visiteur"),
            auteur_role=(utilisateur.libelle_role if utilisateur and utilisateur.is_authenticated
                         else "Visiteur"),
        )


                                                                            
                                                       
                                                                            
class ParametresEtablissement(models.Model):
    nom_etablissement = models.CharField(
        "nom de l'établissement", max_length=250,
        default="École Polytechnique de Thiès",
    )
    sigle = models.CharField("sigle", max_length=30, default="EPT")
    ville = models.CharField("ville", max_length=100, default="Thiès")
    pays = models.CharField("pays", max_length=100, default="Sénégal")
    annee_universitaire = models.CharField("année universitaire", max_length=20,
                                           default="2025-2026")
    directeur_recherche = models.CharField("directeur de la recherche", max_length=200,
                                           blank=True)
    contact_email = models.EmailField("email de contact", blank=True)
    site_web = models.URLField("site web", max_length=300, blank=True)
    devise = models.CharField("devise de l'école", max_length=250, blank=True)

    class Meta:
        verbose_name = "paramètres de l'établissement"
        verbose_name_plural = "paramètres de l'établissement"

    def __str__(self):
        return self.nom_etablissement

    @classmethod
    def charger(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
