from rest_framework import serializers

from platform_app.models import Offer, Order, Review


class OfferSerializer(serializers.ModelSerializer):
    
    
    
    class Meta:
            model= Offer


        
        
        
class OrderSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model= Order
        
        
        
class ReviewSerializer(serializers.ModelSerializer):
    
    
    class Meta:
        model= Review
        
        
