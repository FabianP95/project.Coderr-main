from rest_framework import serializers

from orders_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for creating orders and updating their status.

    On create only offer_detail_id is accepted, on update only the status.
    """

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
        """Adjust the fields depending on the view action.

        On create the status is read only, for all other actions
        offer_detail_id is removed.
        """
        super().__init__(*args, **kwargs)
        view = self.context.get("view")
        if view is not None and view.action == "create":
            self.fields["status"].read_only = True
        else:
            self.fields.pop("offer_detail_id", None)

    def validate(self, data):
        """Ensure that an update request only contains the status field."""
        if self.instance is not None:
            data_keys = set(self.initial_data.keys())
            if data_keys != {"status"}:
                raise serializers.ValidationError(
                    "Request must only contain the status."
                )
        return data

    def create(self, validated_data):
        """Create an order by copying the data of the given offer detail.

        The offer_detail instance is passed in by the view via serializer.save().
        """
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
