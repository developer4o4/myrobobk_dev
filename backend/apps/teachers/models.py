from django.db import models
from django.utils.text import slugify
from apps.courses.models import Course
from apps.common.models import BaseModel


class Teacher(BaseModel):
    username = models.CharField(max_length=255)
    job = models.CharField(max_length=255)
    about = models.TextField()

    direction = models.CharField(max_length=255, blank=True, null=True)
    experience = models.CharField(max_length=255, blank=True, null=True)
    work_place = models.CharField(max_length=255, blank=True, null=True)

    img = models.FileField(upload_to='user')
    slug = models.SlugField(unique=True, max_length=200, blank=True, null=True)

    courses = models.ManyToManyField(
        Course,
        related_name="teachers",
        blank=True,
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.username)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username