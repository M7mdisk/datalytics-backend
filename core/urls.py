from django.urls import path, include
from .views import RegisterView, DatasetViewSet, login, clean_dataset
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")

urlpatterns = [
    path("datasets/<int:id>/clean/", clean_dataset),
    path("", include(router.urls)),
    path("login/", login),
    path("register/", RegisterView.as_view()),
]
