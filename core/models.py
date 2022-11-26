from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
import pandas as pd
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    pass


class Dataset(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to="datasets/", validators=[FileExtensionValidator(allowed_extensions=["csv", "xlsx", "xls", "xlsm", "xlsb"])])
    cleaned_file = models.FileField(
        upload_to="datasets/cleaned/", null=True, editable=False)
    DATASET_STATUS = [("C", "Cleaned"), ("U", "Unprocessed")]
    status = models.CharField(max_length=1, default="U", editable=False)

    @property
    def df(self):
        extension = self.file.name.split(".")[-1]
        if extension == "csv":
            df = pd.read_csv(self.file)
        elif extension in ["xlsx", "xls", "xlsm", "xlsb"]:
            df = pd.read_excel(self.file)
        else:
            raise Exception("File extention not valid")
        return df

    def __str__(self) -> str:
        return self.file.name


@receiver(post_save, sender=Dataset, dispatch_uid="fill_dataset_columns")
def fill_columns(sender, instance, created, **kwargs):
    if created:
        df = instance.df
        for col in df.columns:
            column = Column(dataset=instance, name=col)
            column.save()
        print(df.describe())


class Column(models.Model):
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="columns")
    name = models.CharField(max_length=1000)
    applied_techniques = models.ManyToManyField(
        'Technique', editable=False)

    def __str__(self) -> str:
        return f"{self.dataset}: {self.name}"


class Technique(models.Model):
    name = models.CharField(max_length=50)
