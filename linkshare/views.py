from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Category, Link, SiteUser
from .serializers import CategorySerializer, LinkSerializer, SiteUserSerializer

class SiteUserViewSet(viewsets.ModelViewSet):
    queryset = SiteUser.objects.all()
    serializer_class = SiteUserSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
