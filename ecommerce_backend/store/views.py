from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer
from rest_framework.permissions import IsAuthenticated

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    @action(detail=True, methods=['post'])
    def add_to_cart(self, request, pk=None):
        product = self.get_object()
        if product.stock > 0:
            product.stock -= 1
            product.save()
            return Response({"message": f"'{product.name}' added to cart."})
        return Response({"error": "Out of stock."}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def remove_from_cart(self, request, pk=None):
        product = self.get_object()
        product.stock += 1
        product.save()
        return Response({"message": f"'{product.name}' removed from cart."})

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=False, methods=['post'])
    def place_order(self, request):
        items = request.data.get('items', [])
        if not items:
            return Response({"error": "Cart is empty."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            total_cost = sum(Product.objects.get(name=item).price for item in items)
            order = Order.objects.create(items=items, total_cost=total_cost)
            return Response({"message": "Order placed.", "order_id": order.id, "total_cost": total_cost})
        except Product.DoesNotExist:
            return Response({"error": "Invalid product in cart."}, status=status.HTTP_400_BAD_REQUEST)