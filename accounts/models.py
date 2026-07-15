from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r'^\+998\d{9}$',
    message="Telefon raqami quyidagi formatda bo'lishi kerak: +998901234567",
)


class UserManager(BaseUserManager):
    """Telefon raqami orqali foydalanuvchi yaratuvchi custom manager."""

    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Telefon raqami kiritilishi shart")
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Superuser is_staff=True bo'lishi kerak")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Superuser is_superuser=True bo'lishi kerak")

        return self.create_user(phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Telefon raqami orqali tizimga kiruvchi custom foydalanuvchi modeli."""

    GENDER_CHOICES = [
        ('erkak', 'Erkak'),
        ('ayol', 'Ayol'),
    ]

    phone_number = models.CharField(
        'telefon raqami', max_length=13, unique=True, validators=[phone_validator]
    )
    full_name = models.CharField('ism', max_length=150, blank=True)
    email = models.EmailField('email', blank=True)
    avatar = models.ImageField('profil rasmi', upload_to='avatars/', blank=True, null=True)
    birth_date = models.DateField("tug'ilgan sana", blank=True, null=True)
    gender = models.CharField('jinsi', max_length=10, choices=GENDER_CHOICES, blank=True)
    bonus_points = models.PositiveIntegerField('bonus ballari', default=0)
    notify_sms = models.BooleanField('SMS xabarlarga rozilik', default=True)
    notify_email = models.BooleanField('Email xabarlarga rozilik', default=True)
    is_active = models.BooleanField('faolmi', default=True)
    is_staff = models.BooleanField('xodimmi', default=False)
    date_joined = models.DateTimeField("ro'yxatdan o'tgan vaqti", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'Foydalanuvchi'
        verbose_name_plural = 'Foydalanuvchilar'
        ordering = ['-date_joined']

    def __str__(self):
        return self.full_name or self.phone_number

    def get_short_name(self):
        return self.full_name or self.phone_number

    @property
    def initial(self):
        """Avatar placeholder uchun bosh harf."""
        name = (self.full_name or '').strip()
        if name:
            return name[0].upper()
        return self.phone_number[-1] if self.phone_number else '?'


class Address(models.Model):
    """Foydalanuvchining yetkazib berish manzili. Bir nechtasi bo'lishi mumkin, bittasi asosiy."""

    user = models.ForeignKey(User, verbose_name='foydalanuvchi', on_delete=models.CASCADE, related_name='addresses')
    region = models.CharField('viloyat', max_length=100)
    district = models.CharField('tuman', max_length=100)
    street = models.CharField("ko'cha, uy", max_length=255)
    landmark = models.CharField("mo'ljal", max_length=255, blank=True)
    phone_number = models.CharField(
        'aloqa uchun telefon', max_length=13, validators=[phone_validator]
    )
    is_default = models.BooleanField('asosiy manzilmi', default=False)

    class Meta:
        verbose_name = 'Manzil'
        verbose_name_plural = 'Manzillar'
        ordering = ['-is_default', 'id']

    def __str__(self):
        return f'{self.region}, {self.district}, {self.street}'

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
