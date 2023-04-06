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
import pandas as pd

from .services.ML import MLModelService,calc_percentage



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

        feature_importance_json = {
            a: b for a, b in zip(feature_names, feature_importance)
        }

        all_predictions = mlservice.get_batch_predictions(
            df[feature_names], generated_model
        )
        df = df.sort_values(by=[target])
        df_categorical_features = df.select_dtypes(include="object")
        if model_type == MLModel.CLASSIFICATION:
            segs = []
            for i,clss in enumerate(generated_model.classes_):
                new_col_name = f"__prediction__val_{clss}"
                df[new_col_name] = all_predictions[:,i]
                s1= df[df[target] == clss].sort_values(by=[new_col_name]).tail(4).describe(include='all')
                most_row = s1.loc['top'].combine_first(s1.loc['max'])
                least_row = s1.loc['top'].combine_first(s1.loc['min'])

                res = {}
                for index, value in most_row.items():
                    if str(index).startswith("__"):
                        res[index] = value
                        continue
                    if index in df_categorical_features:
                        res[index] = least_row[index]
                    else:
                        res[index] = str(least_row[index]) + ' - ' + str(most_row[index])
                
                print(clss)
                print(df[df[target] == clss].sort_values(by=[new_col_name]).tail(5))
                segs.append(pd.Series(res)[feature_names].to_dict())


            idces = all_predictions.argmax(axis=0)
            maxes = all_predictions.max(axis=0)
            # s1= df.tail(5).describe(include='all')
            # segs = [df[feature_names].iloc[x].to_dict() for x in idces]
            segments = {
                a: {"confidence": calc_percentage(c), "values": b}
                for a, b, c in zip(generated_model.classes_, segs, maxes)
            }
        else:
            df["___prediction__val"] = all_predictions.tolist()
            most_important_rows = df.tail(5)
            least_important_rows = df.head(5)
            s1= most_important_rows.describe(include='all')
            most_row = s1.loc['top'].combine_first(s1.loc['mean'])
            most_row_min = s1.loc['top'].combine_first(s1.loc['min'])
            most_row_max = s1.loc['top'].combine_first(s1.loc['max'])


            res_most = {}
            for index, value in most_row_min.items():
                if str(index).startswith("__"):
                    res_most[index] = value
                    continue
                if index in df_categorical_features:
                    res_most[index] = most_row[index]
                else:
                    res_most[index] = str(most_row_min[index]) + ' - ' + str(most_row_max[index])

            s2= least_important_rows.describe(include='all')
            least_row = s2.loc['top'].combine_first(s2.loc['mean'])

            least_row_min = s2.loc['top'].combine_first(s2.loc['min'])
            least_row_max = s2.loc['top'].combine_first(s2.loc['max'])


            res_least = {}
            for index, value in least_row_min.items():
                if str(index).startswith("__"):
                    res_least[index] = value
                    continue
                if index in df_categorical_features:
                    res_least[index] = least_row[index]
                else:
                    res_least[index] = str(least_row_min[index]) + ' - ' + str(least_row_max[index])
            print(res_most)
            print(res_least)

            feature_names.append("___prediction__val")
            # least_row = df.iloc[df["___prediction__val"].idxmin()]
            # most_row = df.iloc[df["___prediction__val"].idxmax()]
            # breakpoint()
            res_least["___prediction__val"] = least_row[target]
            res_most["___prediction__val"] = most_row[target]


            segments = {"most": pd.Series(res_most)[feature_names].to_dict(), "least": pd.Series(res_least)[feature_names].to_dict()}

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
    sklearn_model = ml_model.selected_model
    features = {
        feature.name: feature.encoder for feature in ml_model.features.all()
    }
    data = request.data
    # TODO: Use confidence intervals for regression problems
    model_input = []
    for feature in features:
        feature_value = data[feature]
        encoder = features[feature]
        if type(feature_value) == str and encoder:
            model_input.append(encoder.transform([feature_value])[0])
        else:
            model_input.append(data[feature])

    prediction = sklearn_model.predict([model_input])[0]

    if ml_model.model_type == MLModel.CLASSIFICATION:
        classes = sklearn_model.classes_
        res = sklearn_model.predict_proba([model_input])[0]
        prediction_probabilities = dict(zip(classes, res))
        return Response(
            {
                "prediction": prediction,
                "prediction_probabilities": prediction_probabilities,
            }
        )

    return Response(
        {
            "prediction": prediction,
        }
    )
