# Generated by Django 4.1.3 on 2023-03-15 14:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0006_mlmodel_feature_importance_alter_dataset_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlmodel",
            name="segments",
            field=models.JSONField(default={}, editable=False),
            preserve_default=False,
        ),
    ]
