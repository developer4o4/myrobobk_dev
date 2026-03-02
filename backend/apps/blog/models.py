from django.db import models
from apps.common.models import BaseModel
from django.utils.text import slugify

class Blog(BaseModel):
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=1000)
    img = models.FileField(upload_to='blog')
    slug = models.CharField(max_length=255, unique=True, blank=True)
    views = models.IntegerField(default=0)
    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


