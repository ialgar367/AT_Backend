import uuid
from datetime import timedelta
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


class PasswordResetToken(models.Model):
    """Token para resetear contraseña del usuario"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Token válido por 24 horas
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Verifica si el token es válido (no usado y no expirado)"""
        return not self.used and timezone.now() < self.expires_at

    def __str__(self):
        return f"Reset token for {self.user.username} - {'Valid' if self.is_valid() else 'Invalid'}"
