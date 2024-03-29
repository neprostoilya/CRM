from rest_framework import serializers
from Order.models import Orders

class OrdersSerializer(serializers.ModelSerializer):
    """
    Orders Serializer
    """
    class Meta:
        model = Orders
        fields = ('pk', 'user', 'furniture', 'description', 'status', 'datetime_order',
            'get_title_furniture_ru','get_title_furniture_uz', 'get_description_furniture_ru', 
            'get_description_furniture_uz', 'get_category_furniture_ru', 'get_category_furniture_uz',
            'get_style_furniture_ru', 'get_style_furniture_uz', 
        )
        
    def create(self, validated_data):
        return super().create(validated_data)
