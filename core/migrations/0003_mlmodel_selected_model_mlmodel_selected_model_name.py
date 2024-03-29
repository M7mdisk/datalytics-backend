# Generated by Django 4.1.3 on 2023-02-08 20:41

from django.db import migrations, models
import picklefield.fields


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0002_column_encoder"),
    ]

    operations = [
        migrations.AddField(
            model_name="mlmodel",
            name="selected_model",
            field=picklefield.fields.PickledObjectField(editable=False, null=True),
        ),
        migrations.AddField(
            model_name="mlmodel",
            name="selected_model_name",
            field=models.CharField(editable=False, max_length=10, null=True),
        ),
    ]
