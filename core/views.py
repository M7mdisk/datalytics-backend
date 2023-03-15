from rest_framework import serializers
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import (
    DatasetSerializer,
    CreateDatasetSerializer,
    DetailsDatasetSerializer,
    MLModelSerializer,
    CreateMLModelSerializer,
    DetailsMLModelSerializer,
)
from .models import Dataset, MLModel
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .services.clean import AutoClean
import json
from pandas.io.json import dumps

from .services.ML import MLModelService


# TODO: Categorical data made of numbers (0,1)
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def clean_dataset(request, id):
    dataset = get_object_or_404(Dataset.objects.filter(owner=request.user), pk=id)
    if dataset.status == Dataset.CLEANED:
        return Response("Dataset already cleaned.", 400)

    df = dataset.df

    auto_clean = AutoClean(df, mode="auto", encode_categ=False)

    cleaned_df = auto_clean.output
    diff = auto_clean.diff
    final = {
        col: diff[col][diff[col].notna()].index.to_list() for col in diff.columns.values
    }
    auto_clean.techniques["modified"] = final

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
            name=serializer.validated_data["file"].name,
            owner=self.request.user,
            uncleaned_file=serializer.validated_data["file"],
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
        if self.action == "retrieve":
            return DetailsMLModelSerializer
        return MLModelSerializer

    def perform_create(self, serializer):
        # breakpoint()
        data = serializer.validated_data
        dataset = data["dataset"]

        df = dataset.df
        target = data["target"].name

        # Determine model type (classifcation or regression)
        model_type = MLModelService.get_field_type(df, target)
        feature_names = [x.name for x in data["features"]]

        mlservice = MLModelService(df, data["target"], data["features"])
        best_model, accuracy = mlservice.find_best_model()
        generated_model, feature_importance = mlservice.generate_model(best_model)
        if len(feature_importance) == 1:
            feature_importance = feature_importance[0]
        feature_importance_json = {
            a: b for a, b in zip(feature_names, feature_importance)
        }

        all_predictions = mlservice.get_batch_predictions(
            df[feature_names], generated_model
        )
        df["___prediction__val"] = all_predictions.tolist()
        if model_type == MLModel.CLASSIFICATION:
            idces = all_predictions.argmax(axis=0)
            maxes = all_predictions.max(axis=0)
            segs = [df[feature_names].iloc[x].to_dict() for x in idces]
            segments = {
                a: {"confidence": c, "values": b}
                for a, b, c in zip(generated_model.classes_, segs, maxes)
            }
        else:
            least_row = df.iloc[df["___prediction__val"].idxmin()].to_dict()
            most_row = df.iloc[df["___prediction__val"].idxmax()].to_dict()
            segments = {"most": most_row, "least": least_row}

        s = serializer.save(
            owner=self.request.user,
            model_type=model_type,
            selected_model_name=best_model,
            selected_model=generated_model,
            accuracy=abs(accuracy),
            feature_importance=feature_importance_json,
            segments=segments,
        )
        return s


# TODO: Error handeling, missing keys, etc
@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def get_prediction(request, id):
    ml_model = get_object_or_404(MLModel.objects.filter(owner=request.user), pk=id)
    ml_model: MLModel = ml_model
    # TODO: Use confidence intervals for regression problems
    if ml_model.model_type == MLModel.CLASSIFICATION:
        sklearn_model = ml_model.selected_model
        features = {
            feature.name: feature.encoder for feature in ml_model.features.all()
        }
        data = request.data

        model_input = []
        for feature in features:
            feature_value = data[feature]
            encoder = features[feature]
            if type(feature_value) == str and encoder:
                model_input.append(encoder.transform([feature_value])[0])
            else:
                model_input.append(data[feature])

        classes = sklearn_model.classes_
        res = sklearn_model.predict_proba([model_input])[0]
        prediction = sklearn_model.predict([model_input])[0]
        prediction_probabilities = dict(zip(classes, res))
        return Response(
            {
                "prediction": prediction,
                "prediction_probabilities": prediction_probabilities,
            }
        )
    return Response("Not implemented yet", 500)
