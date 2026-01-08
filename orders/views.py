import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import Order, OrderItem
from products.models import Product
from .serializers import OrderSerializer, OrderItemSerializer

# Helper function
def update_order_total(order):
    total = sum([item.price * item.quantity for item in order.items.all()])
    order.total = total
    order.save()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_cart(request):
    """
    Get user's current cart (incomplete order)
    """
    try:
        # Get or create cart for current user
        order, created = Order.objects.get_or_create(
            user=request.user, 
            completed=False
        )
        
        # If new cart created, initialize total
        if created:
            order.total = 0
            order.save()
            
        serializer = OrderSerializer(order)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """
    Add product to user's cart
    """
    try:
        with transaction.atomic():
            product_id = request.data.get('product_id')
            quantity = int(request.data.get('quantity', 1))

            if not product_id:
                return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

            # Get or create cart for current user
            order, _ = Order.objects.get_or_create(
                user=request.user, 
                completed=False,
                defaults={'total': 0}
            )

            # Check if product already in cart
            order_item, created = OrderItem.objects.get_or_create(
                order=order,
                product=product,
                defaults={'quantity': quantity, 'price': product.price}
            )

            if not created:
                order_item.quantity += quantity
                order_item.save()

            # Update order total
            update_order_total(order)

            serializer = OrderSerializer(order)
            return Response(serializer.data)
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request):
    """
    Remove product from user's cart
    """
    try:
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(user=request.user, completed=False)
        except Order.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = OrderItem.objects.get(order=order, product_id=product_id)
            item.delete()
        except OrderItem.DoesNotExist:
            return Response({'error': 'Item not in cart'}, status=status.HTTP_404_NOT_FOUND)

        update_order_total(order)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decrease_quantity(request):
    """
    Decrease quantity of product in cart (remove if quantity becomes 0)
    """
    try:
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response({'error': 'Product ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(user=request.user, completed=False)
        except Order.DoesNotExist:
            return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            item = OrderItem.objects.get(order=order, product_id=product_id)
            if item.quantity > 1:
                item.quantity -= 1
                item.save()
            else:
                item.delete()
        except OrderItem.DoesNotExist:
            return Response({'error': 'Item not in cart'}, status=status.HTTP_404_NOT_FOUND)

        update_order_total(order)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
        
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def checkout(request):
    """
    Complete the current order and create new empty cart
    """
    try:
        with transaction.atomic():
            # Get current cart
            try:
                order = Order.objects.get(user=request.user, completed=False)
            except Order.DoesNotExist:
                return Response({'error': 'No active cart found'}, status=status.HTTP_404_NOT_FOUND)

            if order.items.count() == 0:
                return Response({'error': 'Cart is empty'}, status=status.HTTP_400_BAD_REQUEST)

            # Mark order as completed
            order.completed = True
            order.save()

            # Create new empty cart for user
            Order.objects.create(user=request.user, completed=False, total=0)

            return Response({
                'success': True,
                'message': 'Order placed successfully!',
                'order_id': order.id,
                'total': order.total
            })
            
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_history(request):
    """
    Get all completed orders for the current user
    """
    orders = Order.objects.filter(
        user=request.user, 
        completed=True
    ).order_by('-created_at')
    
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """
    Get details of a specific order
    """
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        serializer = OrderSerializer(order)
        return Response(serializer.data)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """
    Clear all items from user's cart
    """
    try:
        order = Order.objects.get(user=request.user, completed=False)
        order.items.all().delete()
        order.total = 0
        order.save()
        
        return Response({
            'success': True,
            'message': 'Cart cleared successfully'
        })
    except Order.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=status.HTTP_404_NOT_FOUND)