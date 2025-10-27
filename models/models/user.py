from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser uchun is_staff=True bo‘lishi kerak")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser uchun is_superuser=True bo‘lishi kerak")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    type_choice = (
        ("1", "Admin"),
        ("2", "O'qituvchi"),
        ("3", "Talaba"),
    )
    status_choice = (
        ("1", "Ishlamoqda"),
        ("2", "Ishdan bo'shagan"),
    )
    gender_choice = (
        ("0", "Tanlanmagan"),
        ("1", "Erkak"),
        ("2", "Ayol"),
    )

    type = models.CharField(_('Turi'), choices=type_choice, default='1', max_length=20, blank=True, null=True)
    status = models.CharField(_('Status'), choices=status_choice, default='1', max_length=20, blank=True, null=True)
    gender = models.CharField(_('Jinsi'), choices=gender_choice, default='0', max_length=20, blank=True, null=True)

    first_name = models.CharField(_('Ismi'), max_length=255, blank=True, null=True)
    second_name = models.CharField(_('Familiyasi'), max_length=255, blank=True, null=True)
    third_name = models.CharField(_('Otasini ismi'), max_length=255, blank=True, null=True)

    full_name = models.CharField(_("To'liq F.I.Sh"), max_length=255, blank=True, null=True)
    short_name = models.CharField(_("Qisqa F.I.Sh"), max_length=255, blank=True, null=True)

    image = models.ImageField(_('Profil rasmi'), default='default/user.png', upload_to='User/%Y/%m/%d/', null=True, blank=True)

    mobile = models.CharField(_('Telefon raqami'), max_length=20, null=True, blank=True)
    birth_date = models.DateField(_('Tug‘ilgan sana'), default=None, null=True, blank=True)

    hemis_id_number = models.BigIntegerField(unique=True, db_index=True, null=True, blank=True)
    hemis_id = models.IntegerField(unique=True, db_index=True, null=True, blank=True)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # === Django auth uchun kerakli flaglar ===
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    # === Auth konfiguratsiya ===
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.full_name if self.full_name else self.email




