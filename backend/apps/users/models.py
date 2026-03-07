from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from datetime import timedelta
import random



class UserManager(BaseUserManager):
    def create_user(self, phone, **extra_fields):
        if not phone:
            raise ValueError("Phone required")

        user = self.model(phone=phone, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    phone = models.CharField(max_length=20, unique=True)

    username = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=5000000
        # default=0
    )

    last_name = models.CharField(
        max_length=150,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"

    def __str__(self):
        return self.username



class TelegramOTP(models.Model):

    phone = models.CharField(max_length=20)

    code = models.CharField(max_length=6, unique=True)

    username = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField()

    attempts_left = models.PositiveSmallIntegerField(default=5)

    class Meta:
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["phone"]),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at

    @classmethod
    def generate_code(cls):
        return f"{random.randint(100000, 999999)}"

    @classmethod
    def create_otp(cls, phone, username=None):

        code = cls.generate_code()

        return cls.objects.create(
            phone=phone,
            username=username,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=3)
        )

    def __str__(self):
        return f"{self.phone} - {self.code}"