from django.utils.translation import gettext_lazy as _
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import pandas as pd
from .managers import UserManager
from django.utils.functional import cached_property


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
    uncleaned_file = models.FileField(
        upload_to="datasets/uncleaned/", null=True, editable=False
    )
    CLEANED = "C"
    UNCLEANED = "U"
    DATASET_STATUS = [(CLEANED, "Cleaned"), (UNCLEANED, "Unprocessed")]
    status = models.CharField(max_length=1, default=UNCLEANED, editable=False)
    description = models.CharField(max_length=150, blank=True)
    applied_techniques = models.JSONField(
        "applied_techniques", blank=True, null=True, editable=False
    )

    # TODO: Make this into a cached_property
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

    class Meta:
        ordering = ("-uploaded_at",)


class Column(models.Model):
    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="columns"
    )
    name = models.CharField(max_length=1000)

    def __str__(self) -> str:
        return f"{self.dataset}: {self.name}"


class MLModel(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    BUILDING = "B"
    DONE = "D"
    MODEL_STATUS = [(BUILDING, "Building"), (DONE, "Done")]
    status = models.CharField(
        max_length=1, default=BUILDING, choices=MODEL_STATUS, editable=False
    )

    CLASSIFICATION = "C"
    REGERSSION = "R"
    MODEL_TYPE = [(CLASSIFICATION, "Classification"), (REGERSSION, "Regression")]
    model_type = models.CharField(max_length=1, editable=False, choices=MODEL_TYPE)

    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE, related_name="models"
    )
    target = models.ForeignKey(
        Column, on_delete=models.CASCADE, related_name="predictors"
    )

    features = models.ManyToManyField(Column)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} -> {self.target}"

    class Meta:
        verbose_name = "ML Model"
