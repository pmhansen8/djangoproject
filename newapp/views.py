from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, renderer_classes, permission_classes,throttle_classes
from django.shortcuts import get_object_or_404
from .models import MenuItem,OrderItem,Order,Cart,Category
from rest_framework import status
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .serializers import MenuItemSerializer,UserSerializer,CategorySerializer, OrderSerializer,GetOrderSerializer,AddToCartSerializer,OrderItemSerializer
from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator, EmptyPage
@api_view(['GET','POST'])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        perpage = request.query_params.get('perpage',default = 2)
        page = request.query_params.get('page',default = 1)
        if category_name:
            items = items.filter(category__contains=category_name)
        if to_price:
            items = items.filter(price=to_price)
        if search:
            items = items.filter(title__contains=search)
        if ordering:
            ordering_fields = ordering.split(',')
            items = items.order_by(*ordering_fields)
        paginator = Paginator(items,per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serialized_item = MenuItemSerializer(items, many = True)
        return Response(serialized_item.data)
    elif request.method == 'POST' and request.user.groups.filter(name='Admin').exists():
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
    else:
        return Response({"message":"Not allowed"})

@api_view(['POST'])
@permission_classes([IsAdminUser])
def menupost(request):
    if request.method == 'POST':
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)
    return Response({"message": "Not allowed"}, status=status)







@api_view()
@throttle_classes([AnonRateThrottle])
def throttle_check(request):
    return Response({"message":"successful"})


@api_view
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def throttle_check_auth(request):
    return Response({"message":"for users only"})




@api_view(['GET','POST','DELETE'])
@permission_classes([IsAdminUser])
def manager(request):
    if request.method == 'GET':
        managers = User.objects.filter(groups__name='manager')
        return Response(managers.values())

    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        managers = Group.objects.get(name='manager')
        if request.method == 'POST':
            user.is_staff = True
            user.save()
            managers.user_set.add(user)
            return Response({"message": "posted"})
        elif request.method == 'DELETE':
            managers.user_set.remove(user)
            return Response({"message":"deleted"})
    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET','POST','DELETE'])
def delivery(request):
    if request.method == 'GET' and (request.user.groups.filter(name='manager').exists() or request.user.groups.filter(name='Admin').exists()):
        delivery = User.objects.filter(groups__name='delivery')
        return Response(delivery.values())
    if request.method == 'POST' and (request.user.groups.filter(name='manager').exists() or request.user.groups.filter(name='Admin').exists()):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            delivery = Group.objects.get(name='delivery')
            if request.method == 'POST':
                delivery.user_set.add(user)
                return Response({"message": "posted"})
            elif request.method == 'DELETE':
                delivery.user_set.remove(user)
                return Response({"message":"deleted"})
    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)





@api_view(['POST','GET'])
@permission_classes([IsAdminUser])
def category(request):
    if request.method == 'POST':
        serialized_item = CategorySerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.validated_data, status.HTTP_201_CREATED)


@api_view(['GET'])
def catitems(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


@api_view(['POST','GET'])
def itemstatus(request):
    if request.method == 'GET':
        order = Order.objects.all()
        serializer = GetOrderSerializer(order, many=True)
        return Response(serializer.data)

    if request.method == 'POST' and request.user.groups.filter(name='Delivery').exists():
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            # Deserialize the request data and retrieve the Order object
            order_id = request.data.get('order_id')
            try:
                order = Order.objects.get(id=order_id)
            except Order.DoesNotExist:
                return Response({'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

            # Update the status field of the Order object to True
            order.status = True
            order.save()

            return Response({'message': 'Order status updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({'message': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)






@api_view(['POST'])
@permission_classes([AllowAny])
def newcustomer(request):
    username = request.data['username']
    if username:
        user = get_object_or_404(User, username=username)
        customer = Group.objects.get(name='customers')
        if request.method == 'POST':
            customer.user_set.add(user)
            return Response({"message": "posted"})
        elif request.method == 'DELETE':
            customer.user_set.remove(user)
            return Response({"message":"deleted"})
    return Response({"message":"error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
def addtocart(request):

    if request.method == 'GET':
        cart = Cart.objects.all()
        serializer = AddToCartSerializer(cart, many=True)
        return Response(serializer.data)
    user = request.user
    item_id = request.data.get('item_id')
    quantity = int(request.data.get('quantity', 1))  # Default to 1 if not specified

    if not item_id:
        return Response({'error': 'Item ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve the MenuItem, or return a 404 error if not found
    menu_item = get_object_or_404(MenuItem, id=item_id)

    # Retrieve or create the cart item
    cart_item, created = Cart.objects.get_or_create(
        user=user,
        menuitem=menu_item,
        defaults={
            'quantity': quantity,
            'unit_price': menu_item.price,
            'price': menu_item.price * quantity  # Initial total price
        }
    )

    if not created:
        # Update the existing cart item
        cart_item.quantity += quantity
        cart_item.price = cart_item.unit_price * cart_item.quantity
        cart_item.save()

    return Response({
        'message': 'Added to cart.',
        'item_id': cart_item.menuitem.id,
        'quantity': cart_item.quantity,
        'total_price': cart_item.price
    }, status=status.HTTP_200_OK)


@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def orderitem(request):
    if request.method == 'GET':
        cart = OrderItem.objects.all()
        serializer = OrderItemSerializer(cart, many=True)
        return Response(serializer.data)

    user = request.user
    item_id = request.data.get('item_id')
    quantity = int(request.data.get('quantity', 1))  # Default to 1 if not specified

    if not item_id:
        return Response({'error': 'Item ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

    # Retrieve the cart item or return a 404 error if not found
    cart_item = get_object_or_404(Cart, id=item_id, user=user)

    # Create or update an Order for the user
    order, _ = Order.objects.get_or_create(user=user)

    # Check if an OrderItem already exists with the same MenuItem in this order
    order_item, created = OrderItem.objects.get_or_create(
        order=order,
        menuitem=cart_item.menuitem,
        defaults={
            'quantity': quantity,
            'unit_price': cart_item.unit_price,
            'price': cart_item.unit_price * quantity
        }
    )

    if not created:
        # Update the existing order item
        order_item.quantity += quantity
        order_item.price = order_item.unit_price * order_item.quantity
        order_item.save()

    # Remove the item from Cart
    cart_item.delete()

    return Response({
        'message': 'Item added to order.',
        'item_id': order_item.menuitem.id,
        'quantity': order_item.quantity,
        'total_price': order_item.price
    }, status=status.HTTP_200_OK)








