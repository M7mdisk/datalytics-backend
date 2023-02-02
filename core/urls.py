from django.urls import path, include
from .views import (
    DatasetViewSet,
    MLModelViewSet,
    clean_dataset,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")
router.register(r"models", MLModelViewSet, basename="model")

urlpatterns = [
    path("", include(router.urls)),
    path("datasets/<int:id>/clean/", clean_dataset),
]
