import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import UserMeSerializer, UserUpdateSerializer
from .models import TelegramOTP  # sizdagi model nomi shu bo'lishi kerak
from .serializers import BotCreateOTPSerializer, LoginByCodeSerializer
from .utils import normalize_phone, generate_6digit_code, expires_after


User = get_user_model()


def _bot_secret_ok(request) -> bool:
    # Bot secret header: X-BOT-SECRET: ....
    got = request.headers.get("X-BOT-SECRET", "")
    need = os.getenv("BOT_OTP_SECRET", "")
    return bool(need) and got == need


class BotCreateOTPView(APIView):
    """
    Bot ishlatadi.
    phone + username yuboradi -> DB ga code yozadi -> code ni qaytaradi.
    """
    permission_classes = [permissions.AllowAny]  # secret bilan himoyalaymiz

    def post(self, request):
        if not _bot_secret_ok(request):
            return Response({"detail": "Forbidden"}, status=403)

        s = BotCreateOTPSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        phone = normalize_phone(s.validated_data["phone"])
        username = (s.validated_data.get("username") or "").strip() or None
        ttl = int(s.validated_data.get("ttl_minutes") or 3)

        # unique code bo'lishi uchun bir necha marta urinib ko'ramiz
        code = None
        for _ in range(10):
            c = generate_6digit_code()
            if not TelegramOTP.objects.filter(code=c).exists():
                code = c
                break
        if not code:
            return Response({"detail": "Code generate bo'lmadi, qayta urinib ko'ring."}, status=500)

        # eski OTPlarni shu phone bo'yicha tozalash (xohlasangiz qoldiring)
        TelegramOTP.objects.filter(phone=phone).delete()

        TelegramOTP.objects.create(
            phone=phone,
            code=code,
            username=username,
            expires_at=expires_after(ttl),
            attempts_left=5,
        )

        return Response({"ok": True, "code": code, "expires_in_min": ttl})


class LoginByCodeView(APIView):
    """
    Sayt ishlatadi.
    Faqat code yuboradi -> tekshiradi -> phone ni olib user yaratadi -> JWT beradi.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        s = LoginByCodeSerializer(data=request.data)
        s.is_valid(raise_exception=True)

        code = (s.validated_data["code"] or "").strip()

        otp = TelegramOTP.objects.filter(code=code).first()
        if not otp:
            return Response({"detail": "Code topilmadi yoki ishlatilgan."}, status=400)

        # expire
        if timezone.now() > otp.expires_at:
            otp.delete()
            return Response({"detail": "Code muddati tugagan."}, status=400)

        # attempts (agar siz code'ni 'verify' qilmayotgan bo'lsangiz, attempts shart emas,
        # lekin keyin xatolik bo'lsa ishlatamiz)
        if otp.attempts_left == 0:
            otp.delete()
            return Response({"detail": "Urinishlar tugagan."}, status=400)

        phone = normalize_phone(otp.phone)
        username = (otp.username or "").strip()

        # code 1 marta ishlasin:
        otp.delete()

        # user create/update
        defaults = {}
        # sizning User modelda username field bor bo'lsa, to'ldiramiz
        if hasattr(User, "username") and username:
            defaults["username"] = username

        user, _created = User.objects.get_or_create(phone=phone, defaults=defaults)

        # agar user oldin bor bo'lsa, username bo'sh bo'lsa keyin to'ldirib qo'yamiz
        if hasattr(user, "username") and username and not (user.username or "").strip():
            user.username = username
            user.save(update_fields=["username"])

        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {"id": user.id, "phone": user.phone, "username": getattr(user, "username", None)},
        })
    

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        return Response(UserMeSerializer(request.user).data)

    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(UserMeSerializer(request.user).data)