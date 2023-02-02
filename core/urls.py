from django.urls import path, include
from .views import (
    UserView,
    DatasetViewSet,
    MLModelViewSet,
    login,
    clean_dataset,
    reset_password,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")
router.register(r"models", MLModelViewSet, basename="model")

urlpatterns = [
    path("login/", login),
    path("user/reset_password/", reset_password),
    path("user/", UserView.as_view()),
    path("", include(router.urls)),
    path("datasets/<int:id>/clean/", clean_dataset),
]
