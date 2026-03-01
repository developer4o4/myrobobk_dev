from django.contrib import admin
from django.utils import timezone

from .models import (
    Course,
    Section,
    Topic,
    Problem,
    TestCase,
    Submission,
    CourseSubscription,
)

# =========================
# Inlines
# =========================

class SectionInline(admin.TabularInline):
    model = Section
    extra = 0
    fields = ("order", "title")
    ordering = ("order", "id")
    show_change_link = True


class TopicInline(admin.TabularInline):
    model = Topic
    extra = 0
    fields = ("order", "title", "topic_type", "video_url")
    ordering = ("order", "id")
    show_change_link = True


class TestCaseInline(admin.TabularInline):
    model = TestCase
    extra = 0
    fields = ("id", "is_hidden")
    readonly_fields = ("id",)
    show_change_link = True


# =========================
# Course
# =========================

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "price", "is_active", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("title",)
    ordering = ("-created_at", "id")
    readonly_fields = ("created_at",)
    inlines = (SectionInline,)


# =========================
# Section
# =========================

@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ("id", "course", "order", "title")
    list_filter = ("course",)
    search_fields = ("title", "course__title")
    ordering = ("course_id", "order", "id")
    inlines = (TopicInline,)


# =========================
# Topic
# =========================

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "section", "topic_type", "order", "has_problem")
    list_filter = ("topic_type", "section__course")
    search_fields = ("title", "section__title", "section__course__title")
    ordering = ("section_id", "order", "id")

    def has_problem(self, obj: Topic):
        # topic_type=code bo'lsa odatda problem bo'ladi
        return hasattr(obj, "problem")

    has_problem.boolean = True
    has_problem.short_description = "Problem"


# =========================
# Problem
# =========================

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "topic", "topic_section", "topic_course")
    list_filter = ("topic__section__course",)
    search_fields = ("title", "topic__title", "topic__section__title", "topic__section__course__title")
    ordering = ("topic__section_id", "topic_id", "id")
    inlines = (TestCaseInline,)

    def topic_section(self, obj: Problem):
        return obj.topic.section
    topic_section.short_description = "Section"

    def topic_course(self, obj: Problem):
        return obj.topic.section.course
    topic_course.short_description = "Course"


# =========================
# TestCase
# =========================

@admin.register(TestCase)
class TestCaseAdmin(admin.ModelAdmin):
    list_display = ("id", "problem", "is_hidden")
    list_filter = ("is_hidden", "problem__topic__section__course")
    search_fields = ("problem__title", "problem__topic__title")
    ordering = ("-id",)

    # input/output katta bo'ladi, admin listda ko'rsatmaymiz
    fieldsets = (
        (None, {"fields": ("problem", "is_hidden")}),
        ("Data", {"fields": ("input_data", "output_data")}),
    )


# =========================
# Submission
# =========================

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "problem", "language", "status", "created_at")
    list_filter = ("status", "language", "problem__topic__section__course", "created_at")
    search_fields = (
        "user__phone",
        "problem__title",
        "problem__topic__title",
        "error_message",
    )
    ordering = ("-created_at", "id")
    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("user", "problem", "language", "status")}),
        ("Code", {"fields": ("source_code",)}),
        ("Error", {"fields": ("error_message",)}),
        ("Dates", {"fields": ("created_at",)}),
    )


# =========================
# CourseSubscription
# =========================

@admin.register(CourseSubscription)
class CourseSubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "course",
        "active",
        "started_at",
        "expires_at",
        "is_valid_now",
        "last_billed_at",
    )
    list_filter = ("active", "course", "expires_at")
    search_fields = ("user__phone", "course__title")
    ordering = ("-expires_at", "-id")

    def is_valid_now(self, obj: CourseSubscription):
        return obj.is_valid()

    is_valid_now.boolean = True
    is_valid_now.short_description = "Valid"