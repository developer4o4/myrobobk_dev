
from django.contrib.auth import get_user_model
from rest_framework import serializers

class BotCreateOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=20)
    username = serializers.CharField(max_length=255, required=False, allow_null=True, allow_blank=True)
    ttl_minutes = serializers.IntegerField(required=False, default=3, min_value=1, max_value=10)

class LoginByCodeSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=10)

User = get_user_model()


class UserMeSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "phone",
            "username",
            "first_name",
            "last_name",
            "balance",
            "is_active",
            "is_staff",
        )
        read_only_fields = ("id", "phone", "is_active", "is_staff")


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("first_name", "last_name")