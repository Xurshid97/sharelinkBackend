from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Category, Link, SiteUser
from .serializers import CategorySerializer, LinkSerializer, SiteUserSerializer
from rest_framework.response import Response

class SiteUserViewSet(viewsets.ModelViewSet):
    queryset = SiteUser.objects.all()
    serializer_class = SiteUserSerializer

    '''
    def create(self, request, *args, **kwargs):
        access_token = request.headers.get('AccessToken')
        print('token', access_token)
        if access_token:
            # If access token is provided, check if the user already exists
            existing_user = SiteUser.objects.filter(access_token=access_token).first()

            if existing_user:
                # User already exists, return appropriate response
                serializer = self.get_serializer(existing_user)
                return Response(serializer.data)
            else:
                # If user does not exist, create new user and assign access token
                # serializer = self.get_serializer(data=request.data)
                # serializer.is_valid(raise_exception=True)
                # self.perform_create(serializer)
                # user = serializer.instance
                user = SiteUser.objects.create()
                user.access_token = access_token
                user.save()
                return Response(serializer.data)
        else:
            # If no access token provided, create new user and generate access token
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            user = serializer.instance
            # Generate access token and save
            user.generate_access_token()
            return Response({"access_token": user.access_token}, status=201)
    '''
    def list(self, request, *args, **kwargs):
        queryset = SiteUser.objects.all()
        access_token = request.headers.get('AccessToken')
        print('token', access_token)
        if access_token:
            # If access token is provided, check if the user already exists
            existing_user = SiteUser.objects.filter(access_token=access_token).first()

            if existing_user:
                # User already exists, return appropriate response
                serializer = self.get_serializer(existing_user)
                return Response(serializer.data)
            else:
                # If user does not exist, create new user and assign access token
                # serializer = self.get_serializer(data=request.data)
                # serializer.is_valid(raise_exception=True)
                # self.perform_create(serializer)
                # user = serializer.instance
                user = SiteUser.objects.create()
                user.access_token = access_token
                user.save()
                return Response(serializer.data)
        else:
            # If no access token provided, create new user and generate access token
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            user = serializer.instance
            # Generate access token and save
            user.create_with_access_token()
            return Response({"access_token": user.access_token}, status=201)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
