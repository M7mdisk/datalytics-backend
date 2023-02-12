from rest_framework import serializers
from .models import Dataset, Column
from django.utils.translation import gettext_lazy as _
import json
import pandas as pd
import numpy as np


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ["id", "name"]


class CreateDatasetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dataset
        fields = ["id", "file", "description"]


class DatasetSerializer(serializers.ModelSerializer):
    # columns = serializers.ReadOnlyField(source="column_names")
    columns = ColumnSerializer(many=True)
    size = serializers.IntegerField(source="file.size", read_only=True)

    class Meta:
        model = Dataset
        fields = [
            "id",
            "file_name",
            "description",
            "uploaded_at",
            "status",
            "size",
            "columns",
        ]


class DetailsDatasetSerializer(serializers.ModelSerializer):
    size = serializers.IntegerField(source="file.size", read_only=True)
    url = serializers.CharField(source="file.url")
    data = serializers.SerializerMethodField()
    columns = ColumnSerializer(many=True)

    class Meta:
        model = Dataset
        fields = [
            "file_name",
            "uploaded_at",
            "status",
            "size",
            "columns",
            "data",
            "url",
            "applied_techniques",
        ]

    def get_data(self, dataframe):
        df: pd.DataFrame = dataframe.df
        percent_missing = df.isnull().sum() * 100 / len(df)
        column_info = pd.DataFrame(
            {"column_name": df.columns, "percent_missing": percent_missing}
        )
        column_info = json.loads(column_info.to_json(orient="records"))

        nums_only = df.select_dtypes(include=np.number)
        Q1 = nums_only.quantile(0.25)
        Q3 = nums_only.quantile(0.75)
        IQR = Q3 - Q1
        outlier_mask = (nums_only < (Q1 - 1.5 * IQR)) | (nums_only > (Q3 + 1.5 * IQR))
        outliers = nums_only[outlier_mask]

        outlier_values = {
            col: list(outliers[col].dropna().unique()) for col in outliers
        }

        # Append outlier info to column info
        column_info = [
            {**d, "outliers": outlier_values.get(d["column_name"]) or []}
            for d in column_info
        ]

        data = df.to_json(orient="records")
        return {"data": json.loads(data), "columns": column_info}
