from django.contrib import admin
from .models import SiteUser, Link, Category
# Register your models here.

admin.site.register(SiteUser)
admin.site.register(Category)
admin.site.register(Link)