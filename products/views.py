import requests
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .models import Product
from .serializers import ProductSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def product_list(request):
    """
    Get all products. If database is empty, fetch from FakeStore API and save.
    """
    # Check if we have products in database
    if Product.objects.count() == 0:
        print("Database empty. Fetching products from FakeStore API...")
        try:
            response = requests.get("https://fakestoreapi.com/products", timeout=10)
            if response.status_code == 200:
                products_data = response.json()
                
                for product_data in products_data:
                    # Create product in database
                    Product.objects.create(
                        title=product_data.get('title', ''),
                        price=product_data.get('price', 0),
                        description=product_data.get('description', ''),
                        category=product_data.get('category', 'general'),
                        image=product_data.get('image', '')
                    )
                
                print(f"Successfully saved {len(products_data)} products to database")
            else:
                print(f"Failed to fetch from API: {response.status_code}")
                return Response([])
        except Exception as e:
            print(f"Error fetching products: {e}")
            return Response([])
    
    # Now get products from our database
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_products(request):
    """
    Manually refresh products from FakeStore API (Admin function)
    """
    try:
        # Clear existing products
        Product.objects.all().delete()
        
        # Fetch new products
        response = requests.get("https://fakestoreapi.com/products", timeout=10)
        if response.status_code == 200:
            products_data = response.json()
            
            for product_data in products_data:
                Product.objects.create(
                    title=product_data.get('title', ''),
                    price=product_data.get('price', 0),
                    description=product_data.get('description', ''),
                    category=product_data.get('category', 'general'),
                    image=product_data.get('image', '')
                )
            
            return Response({
                'message': f'Successfully refreshed {len(products_data)} products',
                'count': len(products_data)
            })
        else:
            return Response({'error': 'Failed to fetch from API'}, status=500)
            
    except Exception as e:
        return Response({'error': str(e)}, status=500)