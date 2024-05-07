from rest_framework import serializers
from .models import Category, Link, SiteUser

class SiteUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteUser
        fields = ['id', 'access_token', 'user']

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ['id', 'title', 'url', 'image', 'category']

class CategorySerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'user', 'links']
