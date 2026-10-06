from django.db.models import Min
from rest_framework import serializers

from platform_app.models import Offer, Order, Review, OfferDetail
from user_auth_app.models import User


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:

        model = User

        fields = ["first_name", "last_name", "username"]


class OfferDetailsSerializer(serializers.ModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="offer-detail")

    class Meta:

        model = OfferDetail

        fields = ["id", "url"]


class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
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

    def get_min_delivery_time(self, obj):
        result = obj.details.aggregate(min_time=Min("delivery_time_in_days"))
        return result["min_time"]

    def get_min_price(self, obj):
        result = obj.details.aggregate(min_price=Min("price"))
        return result["min_price"]


class OfferDetailSerializer(serializers.ModelSerializer):
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


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            "id",
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
            "status",
            "created_at",
            "updated_at",
        ]

        read_only_fields = ["customer_user", "business_user"]


class ReviewSerializer(serializers.ModelSerializer):

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
