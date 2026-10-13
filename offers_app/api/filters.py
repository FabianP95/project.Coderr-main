import django_filters
from django_filters import FilterSet

from offers_app.models import Offer


class OfferFilter(FilterSet):
    """Query filters for the offer list.

    min_price and max_delivery_time filter on the annotated
    fields min_price and min_delivery_time of the queryset.
    """

    creator_id = django_filters.NumberFilter(field_name="user__id")
    min_price = django_filters.NumberFilter(field_name="min_price", lookup_expr="gte")
    max_delivery_time = django_filters.NumberFilter(
        field_name="min_delivery_time", lookup_expr="lte"
    )

    class Meta:
        model = Offer
        fields = ["creator_id", "min_price", "max_delivery_time"]
