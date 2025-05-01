from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import uuid
from datetime import timedelta
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    """Custom manager for the CustomUser model."""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'professional')
        extra_fields.setdefault('accepte_conditions', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, username, password, **extra_fields)


def validate_username(value):
    """Validate that username contains only alphanumeric characters or spaces."""
    if not all(char.isalnum() or char.isspace() for char in value):
        raise ValidationError(
            _("Username must contain only letters, numbers, and spaces.")
        )


class CustomUser(AbstractUser):
    PROFESSIONAL = 'professional'
    PARENT = 'parent'
    OTHER = 'other'

    USER_TYPE_CHOICES = [
        (PROFESSIONAL, 'Professional'),
        (PARENT, 'Parent'),
        (OTHER, 'Other'),
    ]

    # Remove the default username field from AbstractUser
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and spaces only.'),
        validators=[validate_username],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that email already exists."),
        }
    )
    user_type = models.CharField(
        _('user type'),
        max_length=12,
        choices=USER_TYPE_CHOICES,
        default='other'
    )
    accepte_conditions = models.BooleanField(
        _('terms accepted'),
        default=False,
        help_text=_('Designates whether the user has accepted the terms and conditions.')
    )
    reset_token = models.UUIDField(
        default=None,
        null=True,
        blank=True,
        editable=False
    )
    reset_token_expiry = models.DateTimeField(
        null=True,
        blank=True
    )
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    last_updated = models.DateTimeField(_('last updated'), auto_now=True)
    security_question = models.CharField(
        max_length=255,
        default="Quel était votre ancien mot de passe ?",
        help_text="Question de sécurité personnalisée"
    )
    security_answer = models.CharField(
        max_length=255,
        blank=True,
        help_text="Réponse à la question de sécurité (hashé)"
    )
    bio = models.BinaryField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        db_table = 'auth_user'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-date_joined']

    def is_parent(self):
        return self.user_type == self.PARENT

    def is_professional(self):
        return self.user_type == self.PROFESSIONAL

    def set_security_answer(self, raw_answer):
        """Hash la réponse comme un mot de passe"""
        from django.contrib.auth.hashers import make_password
        self.security_answer = make_password(raw_answer)

    def verify_security_answer(self, raw_answer):
        """Vérifie comme un mot de passe"""
        from django.contrib.auth.hashers import check_password
        return check_password(raw_answer, self.security_answer)
    def __str__(self):
        return f"{self.username} ({self.email})"

    def clean(self):
        """Additional model-wide validation."""
        super().clean()
        if not self.accepte_conditions:
            raise ValidationError(_("You must accept the terms and conditions."))

    def generate_reset_token(self):
        """Generate a password reset token with expiry (24 hours)."""
        self.reset_token = uuid.uuid4()
        self.reset_token_expiry = timezone.now() + timedelta(hours=24)
        self.save()
        return self.reset_token

    def is_reset_token_valid(self):
        """Check if the reset token is still valid."""
        return (self.reset_token is not None and
                self.reset_token_expiry is not None and
                self.reset_token_expiry > timezone.now())

    def clear_reset_token(self):
        """Clear the reset token after use."""
        self.reset_token = None
        self.reset_token_expiry = None
        self.save()

