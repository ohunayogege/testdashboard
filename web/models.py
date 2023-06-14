from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from cloudinary.models import CloudinaryField


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    ACCOUNT_TYPE = (
        ("Fixed Deposit", "Fixed Deposit"),
        ("Savings", "Savings"),
        ("Current", "Current"),
        ("Dormant", "Dormant"),
    )
    GENDER = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    ACCOUNT_STATUS = (
        ("Verified", "Verified"),
        ("Dormant", "Dormant"),
        ("Suspend", "Suspend"),
        ("Pending Verification", "Pending Verification")
    )
    username = models.CharField(max_length=100, unique=True)
    first_name = models.CharField(max_length=100, default='', blank=True)
    last_name = models.CharField(max_length=100, default='', blank=True)
    mobile = models.CharField(max_length=100, default='', blank=True)
    gender = models.CharField(max_length=100, default='Male', blank=True, choices=GENDER)
    account_status = models.CharField(max_length=100, default='Verified', blank=True, choices=ACCOUNT_STATUS)
    bank_branch_code = models.CharField(_("Routine Number"), max_length=100, default='', blank=True)
    account_name = models.CharField(max_length=100, default='', blank=True)
    account_number = models.CharField(max_length=100, default='', blank=True)
    account_type = models.CharField(max_length=100, default='Savings', blank=True, choices=ACCOUNT_TYPE)
    address = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    state = models.CharField(max_length=100, default='', blank=True)
    zip_code = models.CharField(max_length=100, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    photo = CloudinaryField("Photo", folder="bank", blank=True, null=True)
    email = models.EmailField(_("Email Address"), unique=True)
    pin = models.CharField(_("Transaction Pin"), max_length=4, default='', blank=True)
    otp = models.CharField(_("OTP"), max_length=6, default='', blank=True)
    has_pin = models.BooleanField(default=False)

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["first_name", "last_name", "email"]

    objects = UserManager()

    def __str__(self):
        return self.email


class GeneratedAccountNumber(models.Model):
    ACCOUNT_TYPE = (
        ("Fixed Deposit", "Fixed Deposit"),
        ("Savings", "Savings"),
        ("Current", "Current"),
        ("Dormant", "Dormant"),
    )
    bank_branch_code = models.CharField(_("Routine Number"), max_length=100, default='', blank=True)
    account_name = models.CharField(max_length=100, default='', blank=False)
    account_number = models.CharField(max_length=100, default='', blank=True)
    account_type = models.CharField(max_length=100, default='Savings', blank=False, choices=ACCOUNT_TYPE)

    def __str__(self):
        return self.account_name

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    reference = models.CharField(max_length=100, default='')
    transfer_type = models.CharField(max_length=100, default='')
    sender_email = models.CharField(max_length=100, default='')
    receiver_name = models.CharField(max_length=100, default='')
    receiver_bank_name = models.CharField(max_length=100, default='')
    receiver_account_number = models.CharField(max_length=100, default='')
    routine_number = models.CharField(max_length=100, default='', blank=True)
    bank_branch_code = models.CharField(max_length=100, default='', blank=True)
    country = models.CharField(max_length=100, default='', blank=True)
    description = models.TextField(default='', blank=True)
    status = models.CharField(max_length=100, default='')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference} - {self.amount} - {self.transfer_type} - {self.receiver_name}"
