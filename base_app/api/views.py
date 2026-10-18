from django.db.models import Avg
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from offers_app.models import Offer
from reviews_app.models import Review
from user_auth_app.models import User


class BaseInfoView(APIView):
    """Public endpoint returning general statistics about the platform."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return review count, average rating, business profile count and offer count.

        The average rating is rounded to one decimal place and falls back
        to 0 if no reviews exist yet.
        """
        reviews = Review.objects.count()
        business_users = User.objects.filter(type=User.Type.BUSINESS).count()
        offers = Offer.objects.count()
        avg = Review.objects.aggregate(avg_rating=Avg("rating"))["avg_rating"]
        average_rating = round(avg, 1) if avg is not None else 0
        return Response(
            {
                "review_count": reviews,
                "average_rating": average_rating,
                "business_profile_count": business_users,
                "offer_count": offers,
            }
        )
