from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import *
class Image_upload(admin.ModelAdmin):
    list_display = ('id', 'image')

admin.site.register(UploadedImage,Image_upload)
