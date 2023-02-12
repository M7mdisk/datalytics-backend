import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from django.utils.translation import gettext_lazy as _
from django.db import models
from django.core.validators import FileExtensionValidator
from django.utils.functional import cached_property
from authentication.models import User
from django.dispatch import receiver
from picklefield.fields import PickledObjectField


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
        self.file.seek(0)
        return df.copy(deep=True)

    @property
    def column_names(self):
        self.file.seek(0)
        return list(self.df.columns.values)

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
    encoder = PickledObjectField(null=True, editable=False)

    def __str__(self) -> str:
        return f"{self.dataset}: {self.name}"


@receiver(models.signals.post_save, sender=Dataset)
def create_dataset_columns(sender, instance: Dataset, created, *args, **kwargs):
    if created:
        df: pd.DataFrame = instance.df
        columns = [Column(dataset=instance, name=col) for col in df.columns]
        columns = Column.objects.bulk_create(columns)
        categorical_cols = set(df.select_dtypes(exclude=np.number).columns)
        # TODO: VERY SLOW, Improve
        for col in columns:
            if col.name in categorical_cols:
                col.encoder = LabelEncoder().fit(df[col.name])
                col.save()
