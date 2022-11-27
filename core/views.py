from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework import viewsets
from rest_framework import permissions
from .serializers import UserSerializer
from rest_framework.permissions import AllowAny


class RegisterView(CreateAPIView):
    """
    Create new user.
    """

    serializer_class = UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = get_user_model().objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
