from rest_framework import serializers
from .models import Dataset, Column, MLModel
from django.utils.translation import gettext_lazy as _
import json
import pandas as pd
from collections import defaultdict
import numpy as np


class ColumnSerializer(serializers.ModelSerializer):
    values = serializers.SerializerMethodField()
    class Meta:
        model = Column
        fields = ["id", "name","values"]

    def get_values(self,instance: Column):
        if instance.encoder:
            return instance.encoder.classes_
        return None


class CreateDatasetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dataset
        fields = ["id", "file", "description"]


class DatasetSerializer(serializers.ModelSerializer):
    # columns = serializers.ReadOnlyField(source="column_names")
    file_name = serializers.CharField(source="name")
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
    file_name = serializers.CharField(source="name")
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

        data = df.reset_index().to_json(orient="records")
        return {"data": json.loads(data), "columns": column_info}


class CreateMLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = ["id", "name", "dataset", "target", "features"]

    def validate(self, attrs):
        target = attrs["target"]
        features = attrs["features"]
        dataset = attrs["dataset"]
        errors = defaultdict(list)

        # if dataset.status != Dataset.CLEANED:
        #     errors["dataset"].append("Dataset must be cleaned before creating model.")
        #     raise serializers.ValidationError(errors)

        if target.dataset != dataset:
            errors["target"].append("Target must be from same dataset")

        if target in features:
            errors["target"].append("Target cannot be one of the features")

        if any([col.dataset != dataset for col in features]):
            errors["features"] = "All feature columns must be from the same dataset"

        if len(errors):
            raise serializers.ValidationError(errors)

        return super().validate(attrs)

    def to_representation(self, instance):
        serializer = DetailsMLModelSerializer(instance)
        return serializer.data


class MLModelSerializer(serializers.ModelSerializer):
    target = serializers.SlugRelatedField(slug_field="name", read_only=True)
    features = serializers.SlugRelatedField(
        slug_field="name", many=True, read_only=True
    )
    dataset = serializers.SlugRelatedField(slug_field="file_name", read_only=True)

    class Meta:
        model = MLModel
        fields = [
            "id",
            "name",
            "created_at",
            "model_type",
            "status",
            "dataset",
            "target",
            "features",
        ]
        read_only_fields = ["model_type", "status"]


class DetailsMLModelSerializer(serializers.ModelSerializer):
    target = serializers.SlugRelatedField(slug_field="name", read_only=True)
    features = ColumnSerializer(many=True)
    dataset = serializers.SlugRelatedField(slug_field="file_name", read_only=True)
    # TODO: Add details about model accuracy, fields, etc

    class Meta:
        model = MLModel
        fields = [
            "id",
            "name",
            "created_at",
            "model_type",
            "status",
            "dataset",
            "target",
            "features",
            "selected_model_name",
            "accuracy",
            "feature_importance",
            "segments"
        ]
        read_only_fields = ["model_type", "status"]
