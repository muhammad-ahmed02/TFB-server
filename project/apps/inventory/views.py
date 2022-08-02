from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from .serializers import *


class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Products.objects.all()
