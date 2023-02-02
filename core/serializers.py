from rest_framework import serializers
from .models import Dataset, Column, MLModel
from django.utils.translation import gettext_lazy as _
import json
import pandas as pd


class CreateDatasetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dataset
        fields = ["id", "file", "description"]


class DatasetSerializer(serializers.ModelSerializer):
    columns = serializers.ReadOnlyField(source="column_names")
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

    class Meta:
        model = Dataset
        fields = [
            "file_name",
            "uploaded_at",
            "status",
            "size",
            "data",
            "url",
            "applied_techniques",
        ]

    def get_data(self, dataframe):
        df = dataframe.df
        percent_missing = df.isnull().sum() * 100 / len(df)
        missing_value_df = pd.DataFrame(
            {"column_name": df.columns, "percent_missing": percent_missing}
        )
        missing_values_json = missing_value_df.to_json(orient="records")

        data = df.head(10).to_json(orient="records")
        return {"data": json.loads(data), "columns": json.loads(missing_values_json)}


class ColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Column
        fields = ["id", "name"]


class CreateMLModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MLModel
        fields = ["id", "name", "dataset", "target", "features"]

    def validate(self, attrs):
        target = attrs["target"]
        features = attrs["features"]
        dataset = attrs["dataset"]
        errors = {}

        if dataset.status != Dataset.CLEANED:
            errors.setdefault("dataset", []).append(
                "Dataset must be cleaned before creating model."
            )
            raise serializers.ValidationError(errors)

        if target.dataset != dataset:
            errors.setdefault("target", []).append("Target must be from same dataset")

        if target in features:
            errors.setdefault("target", []).append(
                "Target cannot be one of the features"
            )

        if any([col.dataset != dataset for col in features]):
            errors["features"] = "All feature columns must be from the same dataset"
        # TODO: Validate target is not one of the features
        if len(errors):
            raise serializers.ValidationError(errors)

        return super().validate(attrs)


class MLModelSerializer(serializers.ModelSerializer):
    target = serializers.SlugRelatedField(slug_field="name", read_only=True)
    features = serializers.SlugRelatedField(
        slug_field="name", many=True, read_only=True
    )

    class Meta:
        model = MLModel
        fields = [
            "name",
            "created_at",
            "model_type",
            "status",
            "dataset",
            "target",
            "features",
        ]
        read_only_fields = ["model_type", "status"]
