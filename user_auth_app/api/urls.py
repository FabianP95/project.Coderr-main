from django.urls import path

from .views import RegistrationView, CustomLogin

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", CustomLogin.as_view(), name="login"),
]