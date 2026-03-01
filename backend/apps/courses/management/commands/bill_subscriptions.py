from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from django.db import transaction

from apps.courses.models import CourseSubscription, add_one_month
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Bill expired subscriptions: charge balance if possible else deactivate"

    def handle(self, *args, **options):
        now = timezone.now()
        qs = CourseSubscription.objects.select_related("course").filter(active=True, expires_at__lte=now)

        count_ok = 0
        count_off = 0

        for sub in qs:
            with transaction.atomic():
                u = User.objects.select_for_update().get(pk=sub.user_id)
                sub = CourseSubscription.objects.select_for_update().get(pk=sub.pk)

                price = Decimal(sub.course.price)

                if u.balance >= price:
                    u.balance -= price
                    u.save(update_fields=["balance"])

                    base = now
                    sub.expires_at = add_one_month(base)
                    sub.last_billed_at = now
                    sub.active = True
                    sub.save(update_fields=["expires_at", "last_billed_at", "active"])
                    count_ok += 1
                else:
                    sub.active = False
                    sub.save(update_fields=["active"])
                    count_off += 1

        self.stdout.write(self.style.SUCCESS(f"Charged: {count_ok}, Deactivated: {count_off}"))