from django.urls import path
from .views import BotCreateOTPView, LoginByCodeView, MeView

urlpatterns = [
    # Bot -> backend (secret bilan)
    path("auth/bot/create-otp/", BotCreateOTPView.as_view(), name="bot_create_otp"),
    path("auth/login/", LoginByCodeView.as_view(), name="login_by_code"),
    path("auth/me/", MeView.as_view(), name="me"),
]