from django.urls import path, include
from .views import RegisterView, DatasetViewSet, MLModelViewSet, login, clean_dataset
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")
router.register(r"models", MLModelViewSet, basename="model")

urlpatterns = [
    path("datasets/<int:id>/clean/", clean_dataset),
    path("", include(router.urls)),
    path("login/", login),
    path("register/", RegisterView.as_view()),
]
