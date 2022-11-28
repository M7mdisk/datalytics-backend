from rest_framework.generics import CreateAPIView
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import (
    UserSerializer,
    DatasetSerializer,
    CreateDatasetSerializer,
    DetailsDatasetSerializer,
)
from .models import Dataset, Column
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view


class RegisterView(CreateAPIView):
    """
    Create new user.
    """

    serializer_class = UserSerializer


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


class DatasetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows datasets to be viewed or edited.
    """

    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dataset.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateDatasetSerializer
        elif self.action == "retrieve":
            return DetailsDatasetSerializer
        return DatasetSerializer

    def perform_create(self, serializer):
        s = serializer.save(owner=self.request.user)
        for col in s.df.columns:
            Column(name=col, dataset=s).save()
        return s
