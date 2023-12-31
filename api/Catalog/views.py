from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from Catalog.models import Categories, Styles, Furnitures, Gallery
from Catalog.serializers import CategoriesSerializer, \
    StylesSerializer, FurnituresSerializer, GallerySerializer
from Catalog.logics.view_logics import get_subcategories_by_category
    
class CategoriesAPIView(APIView):
    """
    View Categories
    """
    serializer_class = CategoriesSerializer

    def get(self, request):
        """
        Get Categories
        """
        categories = Categories.objects.all().filter(
            subcategory=None
        )
        serializer = CategoriesSerializer(categories, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
class SubcategoriesAPIView(APIView):
    """
    View Subcategories
    """

    def get(self, request, category):
        """
        Get Subcategories
        """
        subcategories = get_subcategories_by_category(
            category=category
        )
        serializer = CategoriesSerializer(subcategories, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class StylesAPIView(APIView):
    """
    View Styles
    """

    def get(self, request):
        """
        Get Styles
        """
        styles = Styles.objects.all()
        serializer = StylesSerializer(styles, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
class FurnituresAPIView(APIView):
    """
    View Furnitures
    """

    def get(self, request, category, style):
        """
        Get Furnitures
        """
        furnitures = Furnitures.objects.filter(
            category=category,
            style=style,
        )
        serializer = FurnituresSerializer(furnitures, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

class GalleryAPIView(APIView):
    """
    View Gallery
    """

    def get(self, request, furniture):
        """
        Get Gallery
        """
        furnitures = Gallery.objects.filter(
            furniture=furniture
        )
        serializer = GallerySerializer(furnitures, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
    
class GetFurnitureAPIView(APIView):
    """
    Get Furniture by pk
    """
    def get(self, request, pk):
        """
        Get Furnitures
        """
        furniture = Furnitures.objects.filter(
            pk=pk
        )
        serializer = FurnituresSerializer(furniture, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
