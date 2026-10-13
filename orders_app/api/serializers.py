from rest_framework import serializers

from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField(write_only=True, min_value=1)

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
            "offer_detail_id",
        ]

        read_only_fields = [
            "customer_user",
            "business_user",
            "title",
            "revisions",
            "delivery_time_in_days",
            "price",
            "features",
            "offer_type",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        view = self.context.get("view")
        if view is not None and view.action == "create":
            self.fields["status"].read_only = True
        else:
            self.fields.pop("offer_detail_id", None)

    def validate(self, data):
        if self.instance is not None:
            data_keys = set(self.initial_data.keys())
            if data_keys != {"status"}:
                raise serializers.ValidationError(
                    "Request must only contain the status."
                )
        return data

    def create(self, validated_data):
        validated_data.pop("offer_detail_id")
        offer_detail = validated_data.pop("offer_detail")
        return Order.objects.create(
            business_user=offer_detail.offer.user,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            **validated_data,
        )
