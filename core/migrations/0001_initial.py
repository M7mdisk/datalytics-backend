# Generated by Django 4.1.3 on 2023-02-02 20:45

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Column",
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
                ("name", models.CharField(max_length=1000)),
            ],
        ),
        migrations.CreateModel(
            name="Dataset",
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
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "file",
                    models.FileField(
                        upload_to="datasets/",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=[
                                    "csv",
                                    "xlsx",
                                    "xls",
                                    "xlsm",
                                    "xlsb",
                                ]
                            )
                        ],
                    ),
                ),
                (
                    "uncleaned_file",
                    models.FileField(
                        editable=False, null=True, upload_to="datasets/uncleaned/"
                    ),
                ),
                ("status", models.CharField(default="U", editable=False, max_length=1)),
                ("description", models.CharField(blank=True, max_length=150)),
                (
                    "applied_techniques",
                    models.JSONField(
                        blank=True,
                        editable=False,
                        null=True,
                        verbose_name="applied_techniques",
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-uploaded_at",),
            },
        ),
        migrations.CreateModel(
            name="MLModel",
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
                ("name", models.CharField(max_length=50)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("B", "Building"), ("D", "Done")],
                        default="B",
                        editable=False,
                        max_length=1,
                    ),
                ),
                (
                    "model_type",
                    models.CharField(
                        choices=[("C", "Classification"), ("R", "Regression")],
                        editable=False,
                        max_length=1,
                    ),
                ),
                (
                    "dataset",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="models",
                        to="core.dataset",
                    ),
                ),
                ("features", models.ManyToManyField(to="core.column")),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "target",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="predictors",
                        to="core.column",
                    ),
                ),
            ],
            options={
                "verbose_name": "ML Model",
            },
        ),
        migrations.AddField(
            model_name="column",
            name="dataset",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="columns",
                to="core.dataset",
            ),
        ),
    ]
