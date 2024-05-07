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
