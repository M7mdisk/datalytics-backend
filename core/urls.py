from django.urls import path, include
from .views import UserViewSet, RegisterView
from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("login/", obtain_auth_token),
    path("register/", RegisterView.as_view()),
]
