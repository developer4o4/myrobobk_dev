from django.db import models
from apps.common.models import BaseModel
from django.utils.text import slugify
from django.conf import settings
User = settings.AUTH_USER_MODEL

class Category(BaseModel):
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255, unique=True, blank=True)
    def save(self, *args, **kwargs):
        if not self.slug: 
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Blog(BaseModel):
    category = models.ForeignKey(Category,on_delete=models.SET_NULL, null=True, blank=True)
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


class Comment(BaseModel):
    blog = models.ForeignKey(
        "Blog",
        on_delete=models.CASCADE,
        related_name="comments"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    text = models.TextField()

    def __str__(self):
        return f"{self.user} - {self.blog.title}"

