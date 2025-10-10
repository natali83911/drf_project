from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from lms.models import Course, Lesson


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email обязателен")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser должен иметь is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None

    email = models.EmailField(unique=True, verbose_name="Почта")

    avatar = models.ImageField(
        upload_to="users/avatars/", verbose_name="Аватар", blank=True, null=True
    )

    phone_number = models.CharField(
        max_length=30, verbose_name="Телефон", blank=True, null=True
    )

    city = models.CharField(max_length=50, verbose_name="Город", blank=True, null=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Payment(models.Model):
    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Дата оплаты")
    paid_course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Оплаченный курс",
    )
    paid_lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="Оплаченный урок",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    payment_method = models.CharField(
        choices=PAYMENT_METHODS, max_length=10, verbose_name="Способ оплаты"
    )
    stripe_product_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Stripe Product ID"
    )
    stripe_price_id = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Stripe Price ID"
    )
    stripe_checkout_session_id = models.CharField(
        max_length=350, blank=True, null=True, verbose_name="Stripe Checkout Session ID"
    )
    payment_url = models.URLField(
        max_length=600, blank=True, null=True, verbose_name="Ссылка для оплаты"
    )
    is_paid = models.BooleanField(default=False, verbose_name="Оплата завершена")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self):
        return f"Платеж #{self.id} от {self.user}"
