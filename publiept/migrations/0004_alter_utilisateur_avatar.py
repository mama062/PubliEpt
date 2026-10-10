                                                

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_alter_enseignant_grade_alter_enseignant_photo"),
    ]

    operations = [
        migrations.AlterField(
            model_name="utilisateur",
            name="avatar",
            field=models.CharField(
                blank=True,
                help_text="Adresse externe (https://…) ou fichier de la plateforme (img/enseignants/nom.jpg).",
                max_length=500,
                verbose_name="photo de profil",
            ),
        ),
    ]
