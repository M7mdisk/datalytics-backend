from rest_framework.generics import CreateAPIView
from rest_framework import serializers
from django.http import HttpResponse
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import (
    UserSerializer,
    DatasetSerializer,
    CreateDatasetSerializer,
    DetailsDatasetSerializer,
    MLModelSerializer,
    CreateMLModelSerializer,
)
from .models import Dataset, Column, MLModel
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.shortcuts import get_object_or_404
from .services.clean import AutoClean
from django.contrib.auth import get_user_model


class RegisterView(CreateAPIView):
    """
    Create new user.
    """

    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        data = response.data
        user = get_user_model().objects.get(id=data["id"])

        token, _ = Token.objects.get_or_create(user=user)

        response.data["token"] = token.key
        return response


@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")
    print(email, password)
    if email and password:
        user = authenticate(email=email, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
    return Response(None, 401)


@api_view(["POST"])
@permission_classes([permissions.IsAuthenticated])
def clean_dataset(request, id):
    dataset = get_object_or_404(Dataset.objects.filter(owner=request.user), pk=id)
    df = dataset.df

    out = AutoClean(df, mode="auto", encode_categ=False)
    dataset.status = Dataset.CLEANED
    # TODO: Save cleaned dataset in dataset.file
    # TODO: Save applied techniques
    dataset.save()
    return HttpResponse(out.output.to_html())


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
        # I know its stupid to save then delete, but it has to be done like this so that df can be accessed
        if s.df.columns.duplicated().any():
            s.delete()
            raise serializers.ValidationError(
                "All columns must be uniquely identifiable (no duplicate column names)"
            )
        for col in s.df.columns:
            Column(name=col, dataset=s).save()
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
