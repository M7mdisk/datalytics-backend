from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import (
    UserSerializer,
    DatasetSerializer,
    CreateDatasetSerializer,
)
from .models import Dataset


class RegisterView(CreateAPIView):
    """
    Create new user.
    """

    serializer_class = UserSerializer


class DatasetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows datasets to be viewed or edited.
    """

    serializer_class = DatasetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Dataset.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CreateDatasetSerializer
        return DatasetSerializer

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)
