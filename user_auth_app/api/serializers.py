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


class UserSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source="id", read_only=True)
    created_at = serializers.DateTimeField(source="date_joined", read_only=True)

    class Meta:
        model = User
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
            "email",
            "created_at",
        ]
        read_only_fields = ["username", "type"]

    def validate_email(self, value):
        existing_users = User.objects.filter(email__iexact=value)

        if self.instance is not None:
            existing_users = existing_users.exclude(pk=self.instance.pk)

        if existing_users.exists():
            raise serializers.ValidationError("Email already exists")
        return value


class BusinessUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "location",
            "tel",
            "description",
            "working_hours",
            "type",
        ]


class CustomerUserSerializer(UserSerializer):
    class Meta:
        model = User
        fields = [
            "user",
            "username",
            "first_name",
            "last_name",
            "file",
            "uploaded_at",
            "type",
        ]
