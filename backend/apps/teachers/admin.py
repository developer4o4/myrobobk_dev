from django.contrib import admin
from django.utils.html import format_html

from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "username",
        "job",
        "direction",
        "experience",
        "work_place",
        "courses_count",
        "image_preview",
        "is_active",
        "created_at",
    )
    list_display_links = ("username", "image_preview")

    search_fields = ("username", "job", "about", "direction", "work_place")
    list_filter = ("is_active", "created_at", "direction", "job")

    # ManyToMany ni admin panelda qulay ko‘rsatadi
    filter_horizontal = ("courses",)

    readonly_fields = ("slug", "image_preview", "courses_count")

    ordering = ("-created_at",)
    list_per_page = 25

    def image_preview(self, obj):
        if obj.img:
            return format_html(
                '<img src="{}" width="70" style="border-radius:6px;object-fit:cover;" />',
                obj.img.url
            )
        return "-"

    image_preview.short_description = "Image"

    def courses_count(self, obj):
        return obj.courses.count()

    courses_count.short_description = "Courses"