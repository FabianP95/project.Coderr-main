"""Serializers for login, registration, and user profile validation."""

# "re" and "AbstractUser" were removed: the regex is replaced by DRF's EmailField
# and AbstractUser is only needed in models.py.
from django.contrib.auth import authenticate
from rest_framework import serializers

from user_auth_app.models import User


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")

        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid username or password")

        data["user"] = user
        return data


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]

        extra_kwargs = {
            "email": {"required": True, "allow_blank": False},
        }

    def validate_email(self, value):

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already exists")

        return value

    def validate(self, data):

        if data["password"] != data["repeated_password"]:

            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match"}
            )

        return data

    def create(self, validated_data):

        validated_data.pop("repeated_password")

        user = User.objects.create_user(**validated_data)

        return user
