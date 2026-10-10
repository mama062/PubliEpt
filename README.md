# PubliEPT — Plateforme de gestion des publications scientifiques

Application web développée avec **Django 5** pour l'École Polytechnique de Thiès (EPT, Sénégal),
dans le cadre du module **Développement Web 2** (Master 1 MILIA).

Elle centralise les publications des enseignants-chercheurs, rend la recherche immédiate et
sans compte, et fournit à l'administration un tableau de bord de pilotage.

La base livrée contient les **publications réelles de onze enseignants-chercheurs de l'EPT**
(voir la section 9).

---

## 1. Installation

Prérequis : **Python 3.10 ou supérieur**. Aucune base de données à installer (SQLite).

```bash
# 1. Se placer dans le dossier du projet
cd publiept_django

# 2. Créer et activer un environnement virtuel
python -m venv venv
source venv/bin/activate          # Linux / macOS
venv\Scripts\activate             # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Appliquer les migrations
python manage.py migrate

# 5. Lancer le serveur
python manage.py runserver
```

L'application est alors disponible sur **http://127.0.0.1:8000/**

---

## 2. Comptes de démonstration

Mot de passe commun : **`publiept2026`**

| Profil | Identifiant | Accès |
|---|---|---|
| **Visiteur** | *aucun compte* | Recherche et consultation du catalogue |
| **Enseignant-chercheur** | `oniang@ept.edu.sn` | Dépôt et gestion de ses publications |
| **Administrateur** | `recherche@ept.sn` | Statistiques, référentiels, comptes |

Chacun des 11 enseignants-chercheurs dispose d'un compte : l'identifiant est son adresse
email (`fngom@ept.edu.sn`, `aguisse@ept.edu.sn`, `aaciss@ept.edu.sn`, etc.). La page de
connexion propose aussi des boutons de connexion rapide.

Un compte technique Django peut être créé avec `python manage.py createsuperuser`
pour accéder à `/django-admin/`.

---

## 3. Les trois profils

### Visiteur (sans compte)
C'est le profil le plus fréquent, et la priorité de la plateforme.

- Accueil avec recherche centrale et chiffres clés
- Catalogue : recherche plein texte et filtres combinables (spécialité, année, auteur,
  type, financement), filtrage sans validation manuelle, compteur de résultats permanent
- Fiche de publication : métadonnées, auteurs dans l'ordre, financement, DOI,
  aperçu du document, citation APA et BibTeX
- Navigation par spécialité, annuaire et profils publics des enseignants

### Enseignant-chercheur
Un compte se crée depuis `/inscription/`, avec une adresse `@ept.edu.sn` (section 6).

- Tableau de bord personnel avec graphique de production
- Liste de ses publications, avec filtres
- **Formulaire de dépôt en 5 étapes** : informations, auteurs ordonnés,
  financement, fichier, récapitulatif
- Profil chercheur (grade, spécialité, ORCID, Google Scholar, biographie)

**Une publication est consultable dès son dépôt : il n'y a aucun circuit de validation.**

### Administrateur
- Tableau de bord statistique : production par année, par spécialité et par type,
  part financée, classement des supports et des enseignants
- Toutes les publications, avec détection et fusion des doublons
- Référentiels : spécialités, supports, financements, mots-clés (avec fusion)
- Gestion des enseignants et des comptes utilisateurs
- Import CSV, export BibTeX / CSV / PDF
- Journal d'activité

---

## 4. Modèle de données

Douze relations, traduction directe du modèle logique du projet.

| Modèle | Rôle |
|---|---|
| `Utilisateur` | Compte, avec un rôle unique (enseignant ou administrateur) |
| `Specialite` | Axe principal de classement des publications |
| `Support` | Revue ou conférence |
| `Financement` | Organisme finançant les travaux, classé par catégorie |
| `MotCle` | Mot-clé d'indexation |
| `Enseignant` | Fiche chercheur, rattachée à une seule spécialité |
| `Auteur` | Signataire, interne (lié à un enseignant) ou externe |
| `Publication` | Publication scientifique |
| `AuteurPublication` | **Association portant l'ordre de signature** |
| `PublicationFinancement` | Cofinancement d'une publication |
| `JournalActivite` | Traçabilité des actions |
| `ParametresEtablissement` | Identité de l'école |

### Règles métier implémentées

1. **Un preprint ou une communication n'a ni revue ni journal** : le support reste vide.
   La règle est appliquée dans le formulaire, dans `Publication.save()` et dans l'affichage.
2. **L'ordre des auteurs est significatif** : `AuteurPublication` porte l'attribut `ordre`
   et l'indicateur d'auteur correspondant ; l'ordre est modifiable à l'écran.
3. **Le DOI est unique lorsqu'il est renseigné** : cela évite qu'un même article soit
   déposé deux fois par deux co-auteurs de l'école.
4. **Un auteur est interne ou externe** : l'auteur interne pointe vers un enseignant, ce
   qui permet de retrouver tous ses travaux même déposés par un collègue.
5. **Une publication peut être cofinancée** par plusieurs organismes.
6. **Un compte se désactive, il ne se supprime jamais**, afin de préserver l'historique.
7. **Chaque organisme financeur relève d'une catégorie** de la nomenclature transmise par la
   direction de la recherche (voir ci-dessous).
8. **La plateforme est réservée à l'EPT** : seule une adresse `@ept.edu.sn` permet de
   créer un compte (section 6).
9. **Aucune photographie n'est inventée** : un enseignant sans photographie fournie est
   représenté par ses initiales, jamais par une image d'illustration.

### Catégories de sources de financement

Nomenclature communiquée par la direction de la recherche de l'EPT :

| Catégorie | Organismes présents dans le jeu de données |
|---|---|
| Bailleurs multilatéraux / développement | CEA-MITIC (Banque Mondiale), Union Européenne — Horizon Europe |
| Coopération francophone | Agence Universitaire de la Francophonie (AUF) |
| Institutions panafricaines | Banque Africaine de Développement, UEMOA |
| Coopération bilatérale | USAID PEER Science, Coopération allemande (GIZ / DAAD) |
| Fondations privées | Fondation Mastercard |
| Financement national | FIRST / MESRI Sénégal |

La catégorie sert de filtre dans le catalogue et alimente un graphique dédié du tableau
de bord de l'administration.

---

## 5. Points techniques à présenter

- **Modèle intermédiaire explicite** : `ManyToManyField(through="AuteurPublication")`
  avec contraintes d'unicité sur `(publication, ordre)` et `(publication, auteur)`.
- **Modèle utilisateur personnalisé** : `AbstractUser` étendu avec un champ `role`.
- **Filtrage combinable** construit avec des objets `Q` (`publiept/services.py`).
- **Agrégations** pour le tableau de bord statistique.
- **Contrôle d'accès par rôle** via un décorateur maison (`role_requis`).
- **Journalisation** de toutes les actions d'écriture.
- **Fusion de doublons** dans une transaction atomique, sans perte de données liées.
- **Vues centralisées** dans un module unique (`publiept/views.py`).
- **Validation métier dans le formulaire** : la règle du domaine institutionnel est
  portée par `clean_email()`, pas par du JavaScript contournable.

---

## 6. Création de compte réservée à l'école

La plateforme est celle de l'EPT : **seule une adresse se terminant par
`@ept.edu.sn` permet de créer un compte**. La règle est portée par le modèle
(`publiept/models.py`) et appliquée par le formulaire d'inscription :

```python
DOMAINE_INSTITUTIONNEL = "ept.edu.sn"


def est_adresse_institutionnelle(email):
    return (email or "").strip().lower().endswith("@" + DOMAINE_INSTITUTIONNEL)
```

À l'inscription (`/inscription/`), un compte **enseignant-chercheur** est créé
avec, dans la même transaction :

- sa **fiche chercheur** (nom, spécialité, grade, téléphone) ;
- son **auteur interne**, qui lui permet de signer des publications et de
  retrouver ses travaux même lorsqu'un collègue les dépose.

Sont refusés : une adresse hors du domaine (`gmail.com`, `ept.sn`,
`notept.edu.sn`, `ept.edu.sn.exemple.com`…), une adresse déjà utilisée, un mot
de passe de moins de huit caractères et une confirmation qui ne correspond pas.

---

## 7. Structure du projet

```text
publiept_django/
├── manage.py
├── requirements.txt
├── db.sqlite3                   # Base SQLite livrée avec les données
├── config/                      # Réglages et routes principales
├── publiept/
│   ├── models.py                # Les 12 modèles du MLD
│   ├── forms.py                 # Formulaires, dont l'inscription
│   ├── services.py              # Filtrage, statistiques, exports, import CSV
│   ├── urls.py                  # Routes applicatives
│   ├── views.py                 # Vues de l'application
│   ├── admin.py                 # Administration Django
│   ├── context_processors.py    # Contexte global pour les templates
│   ├── migrations/              # Historique des migrations Django
│   └── templatetags/            # Filtres de gabarit
├── templates/
│   ├── base.html
│   ├── partials/                # Barre latérale, en-tête, cartes, modales
│   ├── public/                  # Espace de consultation
│   ├── enseignant/              # Espace enseignant
│   └── administration/          # Espace administrateur
├── static/
│   ├── css/                     # Tailwind compilé + styles du projet
│   ├── js/                      # Scripts et bibliothèques
│   └── img/enseignants/         # Photographies réellement fournies
└── data/donnees_ept.json        # Jeu de données source de l'EPT
```

---

## 8. Mise en forme

L'interface utilise **Tailwind CSS compilé localement** (`static/css/tailwind.css`) :
aucune connexion Internet n'est nécessaire pour l'affichage. Les icônes (Lucide) et les
graphiques (Chart.js) sont également embarqués dans `static/js/vendor/`.

Le CSS compilé est déjà livré dans ce dépôt. Si vous modifiez les gabarits et ajoutez
de nouvelles classes Tailwind, vous devrez réinstaller un outillage Node local puis
recompiler.

---

## 9. Jeu de données

Le fichier `data/donnees_ept.json` contient des **données réelles de l'EPT**, relevées sur
le site de l'École Doctorale (EDPT) et dans les listes de publications communiquées par les
enseignants-chercheurs.

- **5 spécialités** de recherche (TSI, IAC, CSE, MAM, GSI)
- **11 enseignants-chercheurs** de l'école, avec leur grade et, pour quatre d'entre eux,
  leur photographie officielle — les sept autres sont représentés par leurs initiales
- **36 publications** réelles réparties sur **2003–2022** :
  13 articles de revue, 21 communications de conférence, 2 preprints
- **29 supports** réels (revues et conférences), **66 mots-clés**
- **35 auteurs** : 11 enseignants de l'école et 24 co-auteurs extérieurs
- **9 organismes de financement** couvrant les 6 catégories de la nomenclature

### Ce qui est volontairement vide

Les informations suivantes n'ont **pas** été inventées, parce qu'elles portent sur des
publications réelles de personnes réelles :

| Champ | État | Qui le renseigne |
|---|---|---|
| Résumé de la publication | vide | l'auteur, au dépôt ou en modification |
| Rattachement à un bailleur | vide | l'auteur, au dépôt |
| Nombre de citations et de lectures | à zéro | relevé bibliométrique ultérieur |
| Photographie | 4 sur 11 | l'enseignant, depuis son profil |

L'interface le signale explicitement plutôt que d'afficher un zéro muet : la fiche de
publication propose de compléter le résumé, et le tableau de bord indique
« financements à renseigner par les auteurs ». Le jeu de données démontre ainsi le
fonctionnement de la plateforme sans produire de fausse information bibliographique.

---

## 10. Points restant à confirmer auprès de l'école

**Les catégories de financement sont celles de la direction de la recherche** : elles sont
définitives. Les organismes rattachés à chaque catégorie restent des exemples, à compléter
au fil des projets réels.

**Les cinq spécialités sont une proposition** construite à partir des thématiques de
recherche observées dans les publications. Elles doivent être confrontées à la liste
officielle des spécialités de thèse de l'EDPT (formations IMSI et IDDSTE).

**Quelques coordonnées sont à vérifier** :

- trois adresses email (Niang, Wade, Diouf) ont été reconstituées d'après la convention
  du site de l'école (`initiale + nom @ept.edu.sn`) ;
- l'adresse `fd@ept.edu.sn` attribuée au Pr. Ousmane Seydi provient telle quelle du site
  de l'EDPT et paraît erronée ;
- plusieurs numéros de téléphone reprennent le numéro générique affiché par le site
  (`+221 77 777 77 77`).

**Quatre enseignants n'ont encore aucune publication** dans le jeu de données (Seydi, Dièye,
Wade, Diouf) : leurs listes n'étaient pas disponibles au moment du relevé.

La mise à jour se fait depuis **Administration → Gestion des référentiels** et
**Gestion des enseignants**, ou directement depuis l'interface d'administration Django.
