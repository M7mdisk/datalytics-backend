# Generated by Django 4.1.3 on 2022-12-26 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_alter_dataset_options_mlmodel_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dataset",
            name="status",
            field=models.CharField(
                choices=[("C", "Cleaned"), ("U", "Unprocessed")],
                default="U",
                editable=False,
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="mlmodel",
            name="model_type",
            field=models.CharField(
                choices=[("C", "Classification"), ("R", "Regression")],
                editable=False,
                max_length=1,
            ),
        ),
        migrations.AlterField(
            model_name="mlmodel",
            name="status",
            field=models.CharField(
                choices=[("B", "Building"), ("D", "Done")],
                default="B",
                editable=False,
                max_length=1,
            ),
        ),
    ]
