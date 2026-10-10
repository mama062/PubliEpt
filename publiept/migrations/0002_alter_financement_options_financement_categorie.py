                                                

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="financement",
            options={
                "ordering": ["categorie", "organisme"],
                "verbose_name": "organisme de financement",
                "verbose_name_plural": "organismes de financement",
            },
        ),
        migrations.AddField(
            model_name="financement",
            name="categorie",
            field=models.CharField(
                choices=[
                    ("MULTILATERAL", "Bailleurs multilatéraux / développement"),
                    ("FRANCOPHONE", "Coopération francophone"),
                    ("PANAFRICAIN", "Institutions panafricaines"),
                    ("BILATERAL", "Coopération bilatérale"),
                    ("FONDATION", "Fondations privées"),
                    ("NATIONAL", "Financement national"),
                ],
                default="NATIONAL",
                help_text="Catégorie usuelle de bailleur, utilisée pour les statistiques.",
                max_length=20,
                verbose_name="catégorie de la source",
            ),
        ),
    ]
