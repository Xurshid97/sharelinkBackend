from django.shortcuts import render
# Create your views here.
from rest_framework import viewsets
from yaml import serialize
from .models import Category, Link, SiteUser, Image
from .serializers import CategorySerializer, LinkSerializer, SiteUserSerializer, ImageSerializer
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.exceptions import NotFound


class SiteUserViewSet(viewsets.ModelViewSet):
    queryset = SiteUser.objects.all()
    serializer_class = SiteUserSerializer

    def list(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token and 'userCreateWithoutAccessToken' not in access_token:
            try:
                site_user = SiteUser.objects.get(access_token=access_token)
                serializer = self.serializer_class(site_user)
                return Response(serializer.data)
            except SiteUser.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
            
        elif access_token and 'userCreateWithoutAccessToken' in access_token:
            # check if access token has index 1 after split and is not empty
            userSharedCategories = ""
            if len(access_token.split('userCreateWithoutAccessToken')) == 2:
                userSharedCategories = access_token.split('userCreateWithoutAccessToken')[1].split(',')
                userSharedCategories = [int(category) for category in userSharedCategories if category != '']
                userSharedCategories = ','.join([str(category) for category in userSharedCategories])
                
            user = SiteUser.objects.create()
            user.savedcategories = userSharedCategories
            user.save()
            return Response({"access_token": user.access_token}, status=201)
        return Response({"error": "User not found."}, status=404)
    
    # this post request is for registering user with already access token.
    def create(self, request, *args, **kwargs):
        data = request.data        
        files = request.FILES
        print('files', files)
        access_token = request.headers.get('Authorization')
        username = data['username']
        password = data['password']
        email = None
        if 'email' in data:
            email = data['email']
        
        login_token = None
        if 'log_in_with_token' in access_token:
            login_token = access_token.split('log_in_with_token')[1]
            print('log_in_with_token', login_token)
            # authenticate user if username and password valid
            try:
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    if user.password == password:
                        site_user = SiteUser.objects.get(access_token=login_token)
                        if site_user.user == user:
                            site_user.user = user
                            site_user.save()
                            return Response({"access_token": site_user.access_token, "message": "User authenticated successfully.", "SavedCategories": site_user.savedcategories})
                        else:
                            site_user = SiteUser.objects.get(user=user)
                            return Response({"access_token": site_user.access_token, "message": "User authenticated successfully.", "SavedCategories": site_user.savedcategories})
                    else:
                        return Response({"message": "Invalid password."})
                else:
                    return Response({"message": "User not found."})
            except SiteUser.DoesNotExist:
                return Response({"message": "User not found."})
        elif 'log_in_without_token' in access_token:
            print('log_in_without_token')
            try:
                if User.objects.filter(username=username).exists():
                    user = User.objects.get(username=username)
                    if user.password == password:
                        site_user = SiteUser.objects.get(user=user)
                        return Response({"access_token": site_user.access_token, "message": "User authenticated successfully.", "SavedCategories": site_user.savedcategories})
                    else:
                        return Response({"message": "Invalid password."})
                else:
                    return Response({"message": "User not found."})
            except SiteUser.DoesNotExist:
                return Response({"message": "User not found."})

        elif data and access_token:
            print('access_token', data)
            user = User.objects.filter(username=username).first()
            site_user = SiteUser.objects.get(access_token=access_token)
            if not user and username and password:
                my_user = User.objects.create(username=username, password=password)
                my_user.save()
                site_user.user = my_user
                site_user.email = email
                site_user.image = files.get('image')
                site_user.save()
                return Response({"access_token": site_user.access_token, "message": "User saved successfully."})
            else:
                return Response({"message": "the user is already present go to log in"})
        elif data and not access_token:
            print('not access_token', data)
            if not User.objects.filter(username=username).exists():
                site_user = SiteUser.objects.create()
                my_user = User.objects.create(username=username, password=password)
                my_user.save()
                print(site_user.access_token)
                nsite_user = SiteUser.objects.get(access_token=site_user.access_token)
                nsite_user.user = my_user
                nsite_user.username = username
                nsite_user.password = password
                nsite_user.email = email
                nsite_user.image = files.get('image')
                nsite_user.savedcategories = data.get('savedcategories')
                nsite_user.save()
                return Response({"access_token": nsite_user.access_token, "message": "User saved successfully."})
            else:
                return Response({"message": "the user is already present go to log in"})
        else:
            return Response(serialize.errors)
        
    # delete request for deleting user
    def delete(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization')
        if access_token:
            try:
                site_user = SiteUser.objects.get(access_token=access_token)
                site_user.user.delete()
                site_user.delete()
                return Response({"message": "User deleted successfully."})
            except SiteUser.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
        return Response({"error": "Authorization token missing."}, status=401)

    def patch(self, request, *args, **kwargs):
        data = request.data       
        files = request.FILES
        access_token = request.headers.get('Authorization')
        print(data)
        if 'saveimage' in access_token:
            access_token = access_token.split('saveimage')[0]
            print('access_token', access_token)
            siteUser = SiteUser.objects.get(access_token=access_token)
            siteUser.image = files.get('image')
            siteUser.save()
            return Response({"message": "image saved successfully"})
        elif access_token:
            siteUser = SiteUser.objects.get(access_token=access_token)
            userSharedCategories = ','.join([str(category) for category in data['savedCategories']])
            siteUser.savedcategories = userSharedCategories
            siteUser.save()
            return Response({"message": "categories saved successfully"})
        return Response({"message": "User must have access token"})

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request, *args, **kwargs):
        access_token = request.headers.get('Authorization')
        if 'global_categories' in access_token:
            # also return username
            categories = Category.objects.filter(isPublic=True, isShared=True)
            serialized_categories = []
            for category in categories:
                serialized_category = self.serializer_class(category).data
                if category.globalcategory.name:
                    serialized_category['globalcategory'] = category.globalcategory.name
                else:
                    serialized_category['globalcategory'] = "general"
                if category.user.user:
                    serialized_category['username'] = category.user.user.username
                else:
                    serialized_category['username'] = None
                serialized_categories.append(serialized_category)
            return Response({"categories": serialized_categories}, status=200)
        user_token = None
        category_list = None
        if 'SharedCategoryListSent' in access_token:
            user_token = access_token.split('SharedCategoryListSent')[0]
            category_list = access_token.split('SharedCategoryListSent')[1].split(',')
            if len(category_list) == 1 and category_list[0] == '':
                return Response({"categories": []}, status=200)
            if not user_token and category_list:
                found = [Category.objects.get(id=category_id) for category_id in category_list]
                found = [category for category in found if category.isPublic]
                serializer = self.serializer_class(found, many=True)
                return Response({"categories": serializer.data}, status=200)
            elif user_token and category_list:
                site_user = SiteUser.objects.get(access_token=user_token)
                site_user.savedcategories = category_list
                list_of_categories = list(Category.objects.filter(user=site_user).values_list('id', flat=True))
                # Exclude the user's own categories from the found list
                found = []
                for category_id in category_list:
                    if category_id != '' and int(category_id) not in list_of_categories:
                        found.append(Category.objects.get(id=category_id, isPublic=True))
                
                serializer = self.serializer_class(found, many=True)
                return Response({"categories": serializer.data}, status=200)
        elif access_token:
            try:
                site_user = SiteUser.objects.get(access_token=access_token)
                categories = Category.objects.filter(user=site_user)
                serializer = self.serializer_class(categories, many=True)
                return Response({"categories": serializer.data}, status=200)
            except SiteUser.DoesNotExist:
                return Response({"error": "User not found."}, status=404)
        else:
            # Handle missing access token
            return Response({"error": "Authorization token missing."}, status=401)

    def create(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        if not access_token:
            access_token = None
        
        if data and access_token:
            try:
                name = data['name']
                site_user = SiteUser.objects.get(access_token=access_token)
                category = Category.objects.create(name=name, user=site_user, isPublic=True)
                serializer = self.serializer_class(category)
                return Response({"categories": serializer.data})
            except Exception as e:
                return Response({"error": str(e)})
        
    
    def patch(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        category_id = data.get('id')
        if data and access_token:
            try:
                name = data.get('name')
                category_isPublic = data.get('isPublic')
                site_user = SiteUser.objects.get(access_token=access_token)
                category = Category.objects.get(id=category_id, user=site_user)
                if name or category_isPublic:
                    category.name = name
                    category.isPublic = category_isPublic
                    category.save()
                serializer = self.serializer_class(category)
                return Response({"categories": serializer.data})
            except Category.DoesNotExist:
                return Response({"error": "Category does not exist for the provided user"}, status=404)
            except Exception as e:
                return Response({"error": str(e)})

    def delete(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        if data and access_token:  
            category_id = data.get('id')  
            try:
                site_user = SiteUser.objects.get(access_token=access_token)
                category = Category.objects.get(id=category_id, user=site_user)
                category.delete()
                return Response({"message": "Category deleted successfully."})
            except Category.DoesNotExist:
                return Response({"error": "Category does not exist for the provided user"}, status=404)
            except Exception as e:
                return Response({"error": str(e)})


class LinkViewSet(viewsets.ModelViewSet):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer

    def list(self, request, *args, **kwargs):
        if 'Authorization' not in request.headers:
            return Response({"error": "Authorization header missing"}, status=401)
        authorized = request.headers.get('Authorization').split('broken')
        try:
            # print(authorized)
            if len(authorized) != 2:
                raise ValueError("Authorization header is not formatted correctly")
            access_token = authorized[0]
            categoryId = authorized[1]
            site_user = SiteUser.objects.get(access_token=access_token)
            try:
                category = Category.objects.get(user=site_user, id=categoryId)
                links = Link.objects.filter(category=category)
                serializer = self.serializer_class(links, many=True)
                return Response({"links": serializer.data, "category_name": category.name}, status=200)
            except Category.DoesNotExist:
                print('Category does not exist for the provided user')
                category = Category.objects.get(id=categoryId)
                if category.isPublic:
                    links = Link.objects.filter(category=category)
                    serializer = self.serializer_class(links, many=True)
                    return Response({"links": serializer.data, "category_name": category.name}, status=200)
                else:
                    return Response({"error": "Category is not public"}, status=404)
        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)
        except SiteUser.DoesNotExist:
            category = Category.objects.get(id=categoryId)
            if category.isPublic:
                links = Link.objects.filter(category=category)
                serializer = self.serializer_class(links, many=True)
                return Response({"links": serializer.data, "category_name": category.name}, status=200)
            else:
                return Response({"error": "Category is not public"}, status=404)
            # return Response({"error": "Category does not exist for the provided user"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def create(self, request, *args, **kwargs):
        try:
            data = request.data
            files = request.FILES
            access_token = request.headers.get('Authorization')
            if not access_token:
                return Response({"error": "Authorization header missing"}, status=401)
                
            site_user = SiteUser.objects.get(access_token=access_token)
            print('data', data)
            if data and site_user:
                try:
                    title = data.get('title')
                    url = data.get('url')
                    image = files.get('image')  # Handling file upload
                    categoryId = data.get('category')
                    description = data.get('description')
                    
                    category = Category.objects.get(id=categoryId)
                    link = Link.objects.create(
                        title=title,
                        url=url,
                        image=image,
                        category=category,
                        description=description
                    )
                    link.save()
                    serializer = self.serializer_class(link)
                    return Response({"links": serializer.data}, status=201)
                except Category.DoesNotExist:
                    return Response({"error": "Category does not exist"}, status=404)
                except Exception as e:
                    return Response({"error": str(e)}, status=400)

        except ValueError as ve:
            return Response({"error": str(ve)}, status=400)
        except SiteUser.DoesNotExist:
            return Response({"error": "SiteUser with the provided access token does not exist"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    def delete(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        if data and access_token:
            link_id = data.get('id')
            try:
                site_user = SiteUser.objects.get(access_token=access_token)
                link = Link.objects.get(id=link_id)
                if link.category.user == site_user:
                    link.delete()
                    return Response({"message": "Link deleted successfully."})
                else:
                    return Response({"error": "Link does not exist for the provided user"}, status=404)
            except Link.DoesNotExist:
                return Response({"error": "Link does not exist for the provided user"}, status=404)
            except Exception as e:
                return Response({"error": str(e)})
    
    def patch(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        link_id = data.get('id')
        if data and access_token:
            try:
                title = data.get('title')
                url = data.get('url')
                description = data.get('description')
                site_user = SiteUser.objects.get(access_token=access_token)
                link = Link.objects.get(id=link_id, category__user=site_user)
                # Handling image file upload
                image_file = request.FILES.get('image')
                print(image_file)
                if image_file:
                    link.image = image_file

                # Update other fields
                if title:
                    link.title = title
                if url:
                    link.url = url
                if description:
                    link.description = description

                link.save()

                serializer = self.serializer_class(link)
                return Response({"categories": serializer.data}, status=200)
            except Link.DoesNotExist:
                return Response({"error": "Link does not exist for the provided user"}, status=404)
            except SiteUser.DoesNotExist:
                return Response({"error": "SiteUser with the provided access token does not exist"}, status=404)
            except Exception as e:
                return Response({"error": str(e)}, status=400)
        else:
            return Response({"error": "Invalid data or access token missing"}, status=400)
    
class LinkImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.all()
    serializer_class = ImageSerializer

    def create(self, request, *args, **kwargs):
        data = request.data
        access_token = request.headers.get('Authorization')
        site_user = SiteUser.objects.get(access_token=access_token)
        if data and site_user:
            try:
                image = data['file']
                imager = Image.objects.create(rasm=image)
                imager.save()
                serializer = self.serializer_class(imager)
                return Response({"categories": serializer.data})
            except Exception as e:
                return Response({"error": str(e)})
        return Response({"error": "Authorization token missing."}, status=401)