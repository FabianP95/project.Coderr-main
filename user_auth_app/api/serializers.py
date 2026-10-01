"""Serializers for login, registration, and user profile validation."""

import re
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import authenticate
from rest_framework import serializers

from user_auth_app.models import User




class UserLoginSerializer(serializers.Serializer):
    pass


class RegistrationSerializer(serializers.ModelSerializer):
    pass