from django.contrib import admin
from django.utils.html import format_html

from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "image_preview",
        "views",
        "created_at",
        "is_active",
    )

    list_display_links = (
        "title",
        "image_preview",
    )

    search_fields = (
        "title",
        "description",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    readonly_fields = (
        "slug",
        "views",
        "image_preview",
    )
    
    ordering = (
        "-created_at",
    )

    list_per_page = 20


    def image_preview(self, obj):

        if obj.img:
            return format_html(
                '<img src="{}" width="80" style="border-radius:5px;" />',
                obj.img.url
            )

        return "-"

    image_preview.short_description = "Image"