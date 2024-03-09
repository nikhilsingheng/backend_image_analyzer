from django.db import models
from django.utils import timezone
from PIL import Image
from io import BytesIO

class UploadedImage(models.Model):
    image = models.ImageField(upload_to='uploads/')
    analyzed = models.BooleanField(default=False)
    height = models.FloatField(null=True, blank=True)
    width = models.FloatField(null=True, blank=True)
    speed = models.FloatField(null=True, blank=True)
    speed_flag = models.BooleanField(default=False, blank=True)
    image_height_flag = models.BooleanField(default=False, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        self.updated_at = timezone.now()
        return super(UploadedImage, self).save(*args, **kwargs)
    
