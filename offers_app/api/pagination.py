from rest_framework.pagination import PageNumberPagination


class OfferListPagination(PageNumberPagination):
    """Page number pagination for the offer list, adjustable via ?page_size=."""

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
