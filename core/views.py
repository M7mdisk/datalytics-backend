from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import (
    DatasetSerializer,
    CreateDatasetSerializer,
    DetailsDatasetSerializer,
    MLModelSerializer,
    CreateMLModelSerializer,
)
from .models import Dataset, MLModel
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .services.clean import AutoClean
import json
from pandas.io.json import dumps


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def clean_dataset(request, id):

    dataset = get_object_or_404(Dataset.objects.filter(owner=request.user), pk=id)
    if dataset.status == Dataset.CLEANED:
        return Response("Dataset already cleaned.", 400)

    df = dataset.df

    auto_clean = AutoClean(df, mode="auto", encode_categ=False)

    cleaned_df = auto_clean.output

    # This converts all types to python standard types (int64->int, etc)
    dataset.applied_techniques = json.loads(
        dumps(auto_clean.techniques, double_precision=0)
    )

    file_name = "uploads/datasets/" + dataset.file_name
    with open(file_name, "w+b") as f:
        cleaned_df.to_csv(f, index=False)

    dataset.status = Dataset.CLEANED
    dataset.save()
    dataset.file.seek(0)
    dataset.refresh_from_db()
    return Response(DetailsDatasetSerializer(dataset).data)


class DatasetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows datasets to be viewed or edited.
    """

    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]
    ordering = ("-uploaded_at",)

    def get_queryset(self):
        return Dataset.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateDatasetSerializer
        elif self.action == "retrieve":
            return DetailsDatasetSerializer
        return DatasetSerializer

    def perform_create(self, serializer):

        s: Dataset = serializer.save(
            owner=self.request.user, uncleaned_file=serializer.validated_data["file"]
        )

        if s.df.columns.duplicated().any():
            s.delete()
            raise serializers.ValidationError(
                "All columns must be uniquely identifiable (no duplicate column names)"
            )
        return s


class MLModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ML Models to be viewed or edited.
    """

    serializer_class = MLModelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MLModel.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "create" or self.action == "update":
            return CreateMLModelSerializer
        return MLModelSerializer

    def perform_create(self, serializer):
        # breakpoint()
        data = serializer.validated_data
        dataset = data["dataset"]

        df = dataset.df

        # Determine model type (classifcation or regression)
        model_type = MLModel.REGERSSION
        df_categorical_features = df.select_dtypes(include="object")
        if data["target"].name in df_categorical_features.columns:
            model_type = MLModel.CLASSIFICATION

        print(model_type)
        s = serializer.save(owner=self.request.user, model_type=model_type)

        # TODO: Start model creation process (try different models etc)
        return s
