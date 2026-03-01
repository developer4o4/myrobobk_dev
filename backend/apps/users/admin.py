from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, TelegramOTP


# ======================
# USER ADMIN
# ======================

@admin.register(User)
class UserAdmin(BaseUserAdmin):

    ordering = ("id",)

    list_display = (
        "id",
        "phone",
        "first_name",
        "last_name",
        "balance",
        "is_staff",
        "is_active",
        "date_joined",
    )

    search_fields = (
        "phone",
        "first_name",
        "last_name",
    )

    list_filter = (
        "is_staff",
        "is_active",
        "date_joined",
    )

    readonly_fields = (
        "date_joined",
    )

    fieldsets = (
        ("Asosiy", {
            "fields": (
                "phone",
                "password",
            )
        }),

        ("Shaxsiy info", {
            "fields": (
                "first_name",
                "last_name",
                "username",
                "balance",
            )
        }),

        ("Ruxsatlar", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),

        ("Sanalar", {
            "fields": (
                "last_login",
                "date_joined",
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone",
            ),
        }),
    )


# ======================
# TELEGRAM OTP ADMIN
# ======================

@admin.register(TelegramOTP)
class TelegramOTPAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "phone",
        "code",
        "username",
        "attempts_left",
        "created_at",
        "expires_at",
        "is_expired_status",
    )

    search_fields = (
        "phone",
        "code",
        "username",
    )

    list_filter = (
        "created_at",
        "expires_at",
    )

    readonly_fields = (
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    def is_expired_status(self, obj):
        return obj.is_expired()

    is_expired_status.boolean = True
    is_expired_status.short_description = "Expired"