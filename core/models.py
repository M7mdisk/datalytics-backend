from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
import pandas as pd
from .managers import UserManager


class User(AbstractUser):
    # Change email to be requireed instead of username
    username = None
    email = models.EmailField(_("email address"), unique=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()


class Dataset(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(
        upload_to="datasets/",
        validators=[
            FileExtensionValidator(
                allowed_extensions=["csv", "xlsx", "xls", "xlsm", "xlsb"]
            )
        ],
    )
    cleaned_file = models.FileField(
        upload_to="datasets/cleaned/", null=True, editable=False
    )
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
        return df.copy(deep=True)

    @property
    def file_name(self):
        return self.file.name.split("/")[-1]

    def __str__(self) -> str:
        return self.file.name


class Column(models.Model):
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="columns"
    )
    name = models.CharField(max_length=1000)
    applied_techniques = models.ManyToManyField("Technique", editable=False)

    def __str__(self) -> str:
        return f"{self.dataset}: {self.name}"


class Technique(models.Model):
    name = models.CharField(max_length=50)
    # TODO: Add technique description
