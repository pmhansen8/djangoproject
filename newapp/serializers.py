from rest_framework import serializers
from .models import MenuItem, Category, Order, Cart, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
class MenuItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    price = serializers.IntegerField()
    featured = serializers.BooleanField(default=False)
    category = CategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category','category_id']

    def create(self, validated_data):
        from .models import MenuItem
        return MenuItem.objects.create(**validated_data)
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category']

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['status']

class GetOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

class AddToCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'