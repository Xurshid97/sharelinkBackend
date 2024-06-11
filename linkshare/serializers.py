from rest_framework import serializers
from .models import Category, Link, SiteUser, Image
from django.contrib.auth.models import User

class SiteUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')
    class Meta:
        model = SiteUser
        fields = ['id', 'access_token', 'email', 'image', 'username', 'savedcategories']

class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = '__all__'

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    links = LinkSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = '__all__'
