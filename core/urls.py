from django.urls import path, include
from .views import (
    DatasetViewSet,
    clean_dataset,
)
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")

urlpatterns = [
    path("", include(router.urls)),
    path("datasets/<int:id>/clean/", clean_dataset),
]
