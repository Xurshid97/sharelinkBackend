from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, LinkViewSet, SiteUserViewSet, LinkImageViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'links', LinkViewSet)
router.register(r'images_upload', LinkImageViewSet)
router.register(r'', SiteUserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
