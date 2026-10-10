                                                

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_alter_financement_options_financement_categorie"),
    ]

    operations = [
        migrations.AlterField(
            model_name="enseignant",
            name="grade",
            field=models.CharField(
                choices=[
                    ("Professeur Titulaire", "Professeur Titulaire"),
                    ("Professeur Assimilé", "Professeur Assimilé"),
                    (
                        "Maître de Conférences Titulaire",
                        "Maître de Conférences Titulaire",
                    ),
                    ("Maître de Conférences", "Maître de Conférences"),
                    ("Maître-Assistant", "Maître-Assistant"),
                    ("Enseignant-Chercheur", "Enseignant-Chercheur"),
                    ("Assistant", "Assistant"),
                    ("Chercheur Associé", "Chercheur Associé"),
                ],
                default="Maître-Assistant",
                max_length=60,
                verbose_name="grade académique",
            ),
        ),
        migrations.AlterField(
            model_name="enseignant",
            name="photo",
            field=models.CharField(
                blank=True,
                help_text="URL complète, ou chemin d'un fichier de static/img/enseignants/.",
                max_length=500,
                verbose_name="photo",
            ),
        ),
    ]
