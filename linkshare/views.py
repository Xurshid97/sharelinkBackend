from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Category, Link, SiteUser
from .serializers import CategorySerializer, LinkSerializer, SiteUserSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound

class SiteUserViewSet(viewsets.ModelViewSet):
    queryset = SiteUser.objects.all()
    serializer_class = SiteUserSerializer

    def list(self, request, *args, **kwargs):
        # first get request never sent with access token.
        user = SiteUser.objects.create()
        user.save()
        return Response({"access_token": user.access_token}, status=201)
    
    # this post request is for registering user with already access token.
    def create(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        if data and access_token:
            username = data['username']
            password = data['password']
            user = User.objects.filter(username=username).first()
            site_user = SiteUser.objects.get(access_token=access_token)

            if not user and not site_user.user and username and password:
                my_user = User.objects.create(username=username, password=password)
                my_user.save()
                site_user.user = my_user
                site_user.save()
                return Response({"access_token": site_user.access_token, "message": "User saved successfully."})
            else:
                return Response({"message": "the user is already present go to log in"})
        else:
            return Response(serializer.errors)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    def list(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization')

        if access_token and 'CategoryListSent' in access_token:
            category_list = access_token.split('CategoryListSent')[1].split(',')
            found = [Category.objects.get(id=category_id) for category_id in category_list]
            serializer = self.serializer_class(found, many=True)
            return Response({"categories": serializer.data}, status=200)
        elif access_token:
            try:
                site_user = SiteUser.objects.get(access_token=access_token)
                categories = Category.objects.filter(user=site_user)
                serializer = self.serializer_class(categories, many=True)
                return Response({"categories": serializer.data}, status=200)
            except SiteUser.DoesNotExist:
                pass  # Handle invalid access token gracefully
        else:
            # Handle missing access token
            return Response({"error": "Authorization token missing."}, status=401)

    def create(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        
        if data and access_token:
            try:
                name = data['name']
                site_user = SiteUser.objects.get(access_token=access_token)
                category = Category.objects.create(name=name, user=site_user)
                serializer = self.serializer_class(category)
                return Response({"categories": serializer.data})
            except Exception as e:
                return Response({"error": str(e)})

class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer

    def list(self, request, *args, **kwargs):
        try:
            authorized = request.headers.get('Authorization').split('broken')
            print(authorized)
            if len(authorized) != 2:
                raise ValueError("Authorization header is not formatted correctly")
            access_token = authorized[0]
            categoryId = authorized[1]
            site_user = SiteUser.objects.get(access_token=access_token)
            category = Category.objects.get(user=site_user, id=categoryId)
            links = Link.objects.filter(category=category)
            serializer = self.serializer_class(links, many=True)
            return Response({"links": serializer.data}, status=200)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)
        except SiteUser.DoesNotExist:
            category = Category.objects.get(id=categoryId)
            links = Link.objects.filter(category=category)
            serializer = self.serializer_class(links, many=True)
            return Response({"links": serializer.data}, status=200)
            # return Response({"error": "Category does not exist for the provided user"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            access_token = request.headers.get('Authorization')
            site_user = SiteUser.objects.get(access_token=access_token)
            if data and site_user:
                try:
                    title = data['title']
                    url = data['url']
                    image = data['image']
                    categoryId = data['id']
                    categoryName = Category.objects.get(id=categoryId)
                    link = Link.objects.create(title=title, url=url, image=image, category=categoryName)
                    link.save()
                    serializer = self.serializer_class(link)
                    return Response({"categories": serializer.data})
                except Exception as e:
                    return Response({"error": str(e)})

        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)
        except SiteUser.DoesNotExist:
            return Response({"error": "SiteUser with the provided access token does not exist"}, status=404)
        except Category.DoesNotExist:
            return Response({"error": "Category does not exist for the provided user"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
