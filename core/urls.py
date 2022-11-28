from django.urls import path, include
from .views import RegisterView, DatasetViewSet, login
from rest_framework import routers
from rest_framework.authtoken import views

router = routers.DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", login),
    path("register/", RegisterView.as_view()),
]
