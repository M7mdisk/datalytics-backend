from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework import permissions
from .serializers import UserSerializer
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from django.http import HttpRequest


class UserView(CreateAPIView, RetrieveAPIView, UpdateAPIView):
    """
    User related endpoints
    POST: Create new user
    GET: Get current user info
    PATCH: partially update user data
    """

    serializer_class = UserSerializer
    queryset = get_user_model()

    def get_permissions(self):
        if self.request.method == "POST":
            return []
        return [permissions.IsAuthenticated()]

    def get_object(self):
        return self.request.user

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
def reset_password(request: HttpRequest):
    new_password = request.data.get("new_password")
    user = request.user
    user.set_password(new_password)
    user.save()
    return Response()
