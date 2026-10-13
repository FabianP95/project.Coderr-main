from django.db import transaction
from rest_framework import serializers

from offers_app.models import Offer, OfferDetail
from user_auth_app.models import User


class UserInfoSerializer(serializers.ModelSerializer):
    """Minimal user representation shown inside the offer list."""

    class Meta:
        model = User

        fields = ["first_name", "last_name", "username"]


class OfferDetailsSerializer(serializers.ModelSerializer):
    """Short offer detail representation containing only id and url."""

    url = serializers.HyperlinkedIdentityField(view_name="offer-detail")

    class Meta:
        model = OfferDetail

        fields = ["id", "url"]


class OfferDetailSerializer(serializers.ModelSerializer):
    """Full representation of a single offer detail."""

    class Meta:
        model = OfferDetail
        fields = [
            "id",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]


class OfferReadsSerializer(serializers.ModelSerializer):
    """Read serializer for offers including the annotated minimum values.

    min_price and min_delivery_time are expected to be annotated
    on the queryset by the view.
    """

    details = OfferDetailsSerializer(many=True, read_only=True)
    min_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, coerce_to_string=False, read_only=True
    )
    min_delivery_time = serializers.IntegerField(read_only=True)
    user_details = UserInfoSerializer(source="user", read_only=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "user",
            "title",
            "image",
            "description",
            "created_at",
            "updated_at",
            "details",
            "min_price",
            "min_delivery_time",
            "user_details",
        ]
        read_only_fields = ["user"]

    def __init__(self, *args, **kwargs):
        """Remove user_details from the output unless the view action is list."""
        super().__init__(*args, **kwargs)
        view = self.context.get("view")
        if view is None or view.action != "list":
            self.fields.pop("user_details", None)


class OfferWriteSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating offers with nested details."""

    details = OfferDetailSerializer(many=True)

    class Meta:
        model = Offer
        fields = [
            "id",
            "title",
            "image",
            "description",
            "details",
        ]

    def validate_details(self, value):
        """Validate the offer types of the submitted details.

        On create exactly three details (basic, standard, premium) are required.
        On update every detail must contain a unique offer_type.
        """
        offer_types = [detail.get("offer_type") for detail in value]

        if self.instance is not None:
            if None in offer_types:
                raise serializers.ValidationError(
                    "Each detail must contain an offer_type."
                )
            if len(offer_types) != len(set(offer_types)):
                raise serializers.ValidationError("Duplicate offer_type in details.")
            return value

        required_types = {choice.value for choice in OfferDetail.Type}
        if len(value) != 3 or set(offer_types) != required_types:
            raise serializers.ValidationError(
                "An offer needs exactly 3 details: basic, standard and premium."
            )
        return value

    def create(self, validated_data):
        """Create the offer and its details within a single transaction."""
        details_data = validated_data.pop("details")

        with transaction.atomic():
            offer = Offer.objects.create(**validated_data)
            for detail_data in details_data:
                OfferDetail.objects.create(offer=offer, **detail_data)

        return offer

    def update(self, instance, validated_data):
        """Update the offer and the submitted details within a single transaction.

        Details are matched to the existing ones by their offer_type.
        """
        details_data = validated_data.pop("details", None)

        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            if details_data is not None:
                for detail_data in details_data:
                    detail = instance.details.get(offer_type=detail_data["offer_type"])
                    for attr, value in detail_data.items():
                        setattr(detail, attr, value)
                    detail.save()

        return instance
