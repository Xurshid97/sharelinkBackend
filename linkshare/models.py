import uuid
from django.db import models
from django.contrib.auth.models import User

class SiteUser(models.Model):
    access_token = models.CharField(max_length=36, default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)

    @classmethod
    def create_with_access_token(cls):
        # Create SiteUser instance with a new UUID access token
        access_token = str(uuid.uuid4())
        site_user = cls(access_token=access_token)
        # Save the instance to the database
        site_user.save()
        return site_user
    
    def __str__(self):
        return self.access_token

class Category(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(SiteUser, on_delete=models.CASCADE, related_name='categories', blank=True, null=True)

    def __str__(self):
        return self.name

class Link(models.Model):
    title = models.CharField(max_length=200)
    url = models.URLField()
    image = models.ImageField(upload_to='link_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='links')

    def __str__(self):
        return self.title