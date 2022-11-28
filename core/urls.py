from django.urls import path, include
from .views import RegisterView, DatasetViewSet
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r"datasets", DatasetViewSet, basename="dataset")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", obtain_auth_token),
    path("register/", RegisterView.as_view()),
]
