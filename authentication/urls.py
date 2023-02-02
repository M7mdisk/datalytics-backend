from django.urls import path
from .views import UserView, login, reset_password

urlpatterns = [
    path("login/", login),
    path("user/", UserView.as_view()),
    path("user/reset_password/", reset_password),
]
