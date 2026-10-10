                                                

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="Auteur",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=120, verbose_name="nom")),
                ("prenom", models.CharField(max_length=120, verbose_name="prénom")),
                (
                    "institution",
                    models.CharField(
                        default="École Polytechnique de Thiès (EPT)",
                        max_length=250,
                        verbose_name="institution",
                    ),
                ),
                (
                    "email",
                    models.EmailField(blank=True, max_length=254, verbose_name="email"),
                ),
            ],
            options={
                "verbose_name": "auteur",
                "verbose_name_plural": "auteurs",
                "ordering": ["nom", "prenom"],
            },
        ),
        migrations.CreateModel(
            name="Financement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "organisme",
                    models.CharField(max_length=250, verbose_name="organisme"),
                ),
                (
                    "type_financement",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="type de subvention"
                    ),
                ),
                (
                    "reference_projet",
                    models.CharField(
                        blank=True, max_length=120, verbose_name="référence du projet"
                    ),
                ),
                (
                    "annee_debut",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="année de début"
                    ),
                ),
                (
                    "annee_fin",
                    models.PositiveIntegerField(
                        blank=True, null=True, verbose_name="année de fin"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
            ],
            options={
                "verbose_name": "organisme de financement",
                "verbose_name_plural": "organismes de financement",
                "ordering": ["organisme"],
            },
        ),
        migrations.CreateModel(
            name="JournalActivite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("action", models.CharField(max_length=200, verbose_name="action")),
                (
                    "type_action",
                    models.CharField(
                        choices=[
                            ("creation", "Création"),
                            ("modification", "Modification"),
                            ("suppression", "Suppression"),
                            ("fusion", "Fusion"),
                            ("connexion", "Connexion"),
                            ("import", "Import"),
                            ("export", "Export"),
                        ],
                        max_length=20,
                        verbose_name="type",
                    ),
                ),
                (
                    "entite",
                    models.CharField(
                        choices=[
                            ("Publication", "Publication"),
                            ("Enseignant", "Enseignant"),
                            ("Utilisateur", "Utilisateur"),
                            ("Referentiel", "Référentiel"),
                            ("Parametres", "Paramètres"),
                        ],
                        max_length=30,
                        verbose_name="entité",
                    ),
                ),
                (
                    "entite_id",
                    models.CharField(
                        blank=True, max_length=60, verbose_name="identifiant de l'objet"
                    ),
                ),
                (
                    "auteur_nom",
                    models.CharField(max_length=150, verbose_name="auteur de l'action"),
                ),
                (
                    "auteur_role",
                    models.CharField(blank=True, max_length=40, verbose_name="rôle"),
                ),
                ("details", models.TextField(blank=True, verbose_name="détails")),
                (
                    "date_action",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date"
                    ),
                ),
            ],
            options={
                "verbose_name": "événement du journal",
                "verbose_name_plural": "journal d'activité",
                "ordering": ["-date_action"],
            },
        ),
        migrations.CreateModel(
            name="MotCle",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "libelle",
                    models.CharField(
                        max_length=150, unique=True, verbose_name="libellé"
                    ),
                ),
            ],
            options={
                "verbose_name": "mot-clé",
                "verbose_name_plural": "mots-clés",
                "ordering": ["libelle"],
            },
        ),
        migrations.CreateModel(
            name="ParametresEtablissement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nom_etablissement",
                    models.CharField(
                        default="École Polytechnique de Thiès",
                        max_length=250,
                        verbose_name="nom de l'établissement",
                    ),
                ),
                (
                    "sigle",
                    models.CharField(
                        default="EPT", max_length=30, verbose_name="sigle"
                    ),
                ),
                (
                    "ville",
                    models.CharField(
                        default="Thiès", max_length=100, verbose_name="ville"
                    ),
                ),
                (
                    "pays",
                    models.CharField(
                        default="Sénégal", max_length=100, verbose_name="pays"
                    ),
                ),
                (
                    "annee_universitaire",
                    models.CharField(
                        default="2025-2026",
                        max_length=20,
                        verbose_name="année universitaire",
                    ),
                ),
                (
                    "directeur_recherche",
                    models.CharField(
                        blank=True,
                        max_length=200,
                        verbose_name="directeur de la recherche",
                    ),
                ),
                (
                    "contact_email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email de contact"
                    ),
                ),
                (
                    "site_web",
                    models.URLField(
                        blank=True, max_length=300, verbose_name="site web"
                    ),
                ),
                (
                    "devise",
                    models.CharField(
                        blank=True, max_length=250, verbose_name="devise de l'école"
                    ),
                ),
            ],
            options={
                "verbose_name": "paramètres de l'établissement",
                "verbose_name_plural": "paramètres de l'établissement",
            },
        ),
        migrations.CreateModel(
            name="Specialite",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "code",
                    models.CharField(max_length=12, unique=True, verbose_name="code"),
                ),
                (
                    "libelle",
                    models.CharField(
                        max_length=200, unique=True, verbose_name="libellé"
                    ),
                ),
                (
                    "description",
                    models.TextField(blank=True, verbose_name="description"),
                ),
                (
                    "couleur",
                    models.CharField(
                        default="#1E3A8A", max_length=9, verbose_name="couleur"
                    ),
                ),
                (
                    "icone",
                    models.CharField(
                        blank=True,
                        default="compass",
                        max_length=40,
                        verbose_name="icône",
                    ),
                ),
            ],
            options={
                "verbose_name": "spécialité",
                "verbose_name_plural": "spécialités",
                "ordering": ["code"],
            },
        ),
        migrations.CreateModel(
            name="Support",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "nom",
                    models.CharField(
                        max_length=300, unique=True, verbose_name="nom du support"
                    ),
                ),
                (
                    "type_support",
                    models.CharField(
                        choices=[
                            ("JOURNAL", "Revue / Journal"),
                            ("CONFERENCE", "Conférence"),
                        ],
                        default="JOURNAL",
                        max_length=20,
                        verbose_name="type",
                    ),
                ),
                (
                    "issn_isbn",
                    models.CharField(
                        blank=True, max_length=60, verbose_name="ISSN / ISBN"
                    ),
                ),
                (
                    "editeur",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="éditeur"
                    ),
                ),
                (
                    "pays",
                    models.CharField(blank=True, max_length=100, verbose_name="pays"),
                ),
                (
                    "est_indexe",
                    models.BooleanField(
                        default=False, verbose_name="indexé Scopus / WoS"
                    ),
                ),
                (
                    "facteur_impact",
                    models.FloatField(
                        blank=True, null=True, verbose_name="facteur d'impact"
                    ),
                ),
            ],
            options={
                "verbose_name": "support de publication",
                "verbose_name_plural": "supports de publication",
                "ordering": ["nom"],
            },
        ),
        migrations.CreateModel(
            name="Utilisateur",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={
                            "unique": "A user with that username already exists."
                        },
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[
                            django.contrib.auth.validators.UnicodeUsernameValidator()
                        ],
                        verbose_name="username",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="adresse email"
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("visiteur", "Visiteur Public"),
                            ("enseignant", "Enseignant-Chercheur"),
                            ("administrateur", "Administrateur EPT"),
                        ],
                        default="enseignant",
                        max_length=20,
                        verbose_name="rôle",
                    ),
                ),
                (
                    "telephone",
                    models.CharField(
                        blank=True, max_length=40, verbose_name="téléphone"
                    ),
                ),
                (
                    "avatar",
                    models.URLField(
                        blank=True, max_length=500, verbose_name="photo de profil"
                    ),
                ),
                (
                    "est_actif",
                    models.BooleanField(
                        default=True,
                        help_text="Un compte se désactive, il ne se supprime jamais.",
                        verbose_name="compte actif",
                    ),
                ),
                (
                    "date_creation",
                    models.DateField(
                        default=django.utils.timezone.now,
                        verbose_name="date de création",
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "utilisateur",
                "verbose_name_plural": "utilisateurs",
                "ordering": ["last_name", "first_name"],
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="AuteurPublication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "ordre",
                    models.PositiveIntegerField(
                        default=1, verbose_name="ordre de signature"
                    ),
                ),
                (
                    "est_auteur_correspondant",
                    models.BooleanField(
                        default=False, verbose_name="auteur correspondant"
                    ),
                ),
                (
                    "auteur",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lignes_publications",
                        to="core.auteur",
                    ),
                ),
            ],
            options={
                "verbose_name": "auteur d'une publication",
                "verbose_name_plural": "auteurs des publications",
                "ordering": ["ordre"],
            },
        ),
        migrations.CreateModel(
            name="Enseignant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nom", models.CharField(max_length=120, verbose_name="nom")),
                ("prenom", models.CharField(max_length=120, verbose_name="prénom")),
                (
                    "email",
                    models.EmailField(
                        max_length=254, unique=True, verbose_name="email institutionnel"
                    ),
                ),
                (
                    "grade",
                    models.CharField(
                        choices=[
                            ("Professeur Titulaire", "Professeur Titulaire"),
                            ("Maître de Conférences", "Maître de Conférences"),
                            ("Maître-Assistant", "Maître-Assistant"),
                            ("Assistant", "Assistant"),
                            ("Chercheur Associé", "Chercheur Associé"),
                        ],
                        default="Maître-Assistant",
                        max_length=60,
                        verbose_name="grade académique",
                    ),
                ),
                (
                    "orcid",
                    models.CharField(
                        blank=True, max_length=40, verbose_name="identifiant ORCID"
                    ),
                ),
                (
                    "google_scholar",
                    models.URLField(
                        blank=True, max_length=400, verbose_name="profil Google Scholar"
                    ),
                ),
                (
                    "biographie",
                    models.TextField(
                        blank=True, verbose_name="biographie scientifique"
                    ),
                ),
                (
                    "photo",
                    models.URLField(blank=True, max_length=500, verbose_name="photo"),
                ),
                (
                    "telephone",
                    models.CharField(
                        blank=True, max_length=40, verbose_name="téléphone"
                    ),
                ),
                (
                    "bureau",
                    models.CharField(
                        blank=True, max_length=200, verbose_name="bureau / laboratoire"
                    ),
                ),
                (
                    "citations_total",
                    models.PositiveIntegerField(
                        default=0, verbose_name="citations totales"
                    ),
                ),
                (
                    "h_index",
                    models.PositiveIntegerField(default=0, verbose_name="indice h"),
                ),
                (
                    "utilisateur",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="enseignant",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="compte utilisateur",
                    ),
                ),
                (
                    "specialite",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="enseignants",
                        to="core.specialite",
                        verbose_name="spécialité",
                    ),
                ),
            ],
            options={
                "verbose_name": "enseignant-chercheur",
                "verbose_name_plural": "enseignants-chercheurs",
                "ordering": ["nom", "prenom"],
            },
        ),
        migrations.AddField(
            model_name="auteur",
            name="enseignant",
            field=models.OneToOneField(
                blank=True,
                help_text="Vide pour un auteur externe à l'établissement.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="profil_auteur",
                to="core.enseignant",
                verbose_name="enseignant EPT",
            ),
        ),
        migrations.CreateModel(
            name="Publication",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("titre", models.CharField(max_length=500, verbose_name="titre")),
                ("resume", models.TextField(blank=True, verbose_name="résumé")),
                (
                    "type_publication",
                    models.CharField(
                        choices=[
                            ("JOURNAL", "Article de Revue"),
                            ("CONFERENCE", "Conférence"),
                            ("COMMUNICATION", "Communication"),
                            ("PREPRINT", "Preprint"),
                        ],
                        default="JOURNAL",
                        max_length=20,
                        verbose_name="type",
                    ),
                ),
                (
                    "annee",
                    models.PositiveIntegerField(verbose_name="année de parution"),
                ),
                (
                    "volume",
                    models.CharField(blank=True, max_length=40, verbose_name="volume"),
                ),
                (
                    "numero",
                    models.CharField(blank=True, max_length=40, verbose_name="numéro"),
                ),
                (
                    "pages",
                    models.CharField(blank=True, max_length=60, verbose_name="pages"),
                ),
                (
                    "doi",
                    models.CharField(
                        blank=True,
                        help_text="Unique lorsqu'il est renseigné : évite les doublons entre co-auteurs.",
                        max_length=200,
                        null=True,
                        unique=True,
                        verbose_name="identifiant DOI",
                    ),
                ),
                (
                    "lien",
                    models.URLField(
                        blank=True, max_length=600, verbose_name="lien officiel"
                    ),
                ),
                (
                    "fichier_pdf",
                    models.CharField(
                        blank=True, max_length=400, verbose_name="chemin du PDF"
                    ),
                ),
                (
                    "pdf_nom",
                    models.CharField(
                        blank=True, max_length=250, verbose_name="nom du fichier"
                    ),
                ),
                (
                    "pdf_taille",
                    models.CharField(
                        blank=True, max_length=30, verbose_name="taille du fichier"
                    ),
                ),
                (
                    "est_financee",
                    models.BooleanField(
                        default=False, verbose_name="publication financée"
                    ),
                ),
                (
                    "date_depot",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date de dépôt"
                    ),
                ),
                (
                    "date_modification",
                    models.DateTimeField(
                        auto_now=True, verbose_name="dernière modification"
                    ),
                ),
                (
                    "citations_count",
                    models.PositiveIntegerField(default=0, verbose_name="citations"),
                ),
                (
                    "lectures_count",
                    models.PositiveIntegerField(default=0, verbose_name="lectures"),
                ),
                (
                    "auteurs",
                    models.ManyToManyField(
                        related_name="publications",
                        through="core.AuteurPublication",
                        to="core.auteur",
                        verbose_name="auteurs",
                    ),
                ),
                (
                    "deposant",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="depots",
                        to="core.enseignant",
                        verbose_name="enseignant déposant",
                    ),
                ),
                (
                    "mots_cles",
                    models.ManyToManyField(
                        blank=True,
                        related_name="publications",
                        to="core.motcle",
                        verbose_name="mots-clés",
                    ),
                ),
            ],
            options={
                "verbose_name": "publication",
                "verbose_name_plural": "publications",
                "ordering": ["-annee", "-date_depot"],
            },
        ),
        migrations.AddField(
            model_name="auteurpublication",
            name="publication",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="lignes_auteurs",
                to="core.publication",
            ),
        ),
        migrations.CreateModel(
            name="PublicationFinancement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "financement",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lignes_publications",
                        to="core.financement",
                    ),
                ),
                (
                    "publication",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="lignes_financements",
                        to="core.publication",
                    ),
                ),
            ],
            options={
                "verbose_name": "financement d'une publication",
                "verbose_name_plural": "financements des publications",
            },
        ),
        migrations.AddField(
            model_name="publication",
            name="financements",
            field=models.ManyToManyField(
                blank=True,
                related_name="publications",
                through="core.PublicationFinancement",
                to="core.financement",
                verbose_name="financements",
            ),
        ),
        migrations.AddField(
            model_name="publication",
            name="specialite",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="publications",
                to="core.specialite",
                verbose_name="spécialité",
            ),
        ),
        migrations.AddField(
            model_name="publication",
            name="support",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="publications",
                to="core.support",
                verbose_name="support de parution",
            ),
        ),
        migrations.AddConstraint(
            model_name="auteurpublication",
            constraint=models.UniqueConstraint(
                fields=("publication", "ordre"), name="ordre_unique_par_publication"
            ),
        ),
        migrations.AddConstraint(
            model_name="auteurpublication",
            constraint=models.UniqueConstraint(
                fields=("publication", "auteur"), name="auteur_unique_par_publication"
            ),
        ),
        migrations.AddConstraint(
            model_name="publicationfinancement",
            constraint=models.UniqueConstraint(
                fields=("publication", "financement"),
                name="financement_unique_par_publication",
            ),
        ),
    ]
