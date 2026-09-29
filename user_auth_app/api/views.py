
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework import status



class CustomLogin(ObtainAuthToken):
    permission_classes = [AllowAny]

    pass


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    pass

