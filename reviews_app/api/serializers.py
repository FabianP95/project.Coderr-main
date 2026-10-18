from rest_framework import serializers

from reviews_app.models import Review
from user_auth_app.models import User


class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for creating, reading and updating reviews."""

    class Meta:
        model = Review
        fields = [
            "id",
            "business_user",
            "reviewer",
            "rating",
            "description",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["reviewer"]
        extra_kwargs = {"description": {"required": True}}

    def validate_business_user(self, value):
        """Ensure that only business users can be reviewed on create."""
        view = self.context.get("view")
        is_create = self.instance is None and view.action == "create"
        if is_create and value.type != User.Type.BUSINESS:
            raise serializers.ValidationError(
                "The profile you want to review must be a business."
            )

        return value

    def validate(self, data):
        """Reject requests containing fields that are not allowed.

        Create accepts business_user, rating and description,
        update only accepts rating and description.
        """
        view = self.context.get("view")
        data_keys = set(self.initial_data.keys())

        is_create = self.instance is None and view.action == "create"
        is_update = self.instance is not None and view.action in (
            "update",
            "partial_update",
        )

        if is_create and not data_keys <= {"business_user", "rating", "description"}:
            raise serializers.ValidationError("Request data not valid.")

        if is_update and not data_keys <= {"rating", "description"}:
            raise serializers.ValidationError("Request data not valid.")
        return data
