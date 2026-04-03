from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='profiles')
    name = models.CharField(
        max_length=100,
        validators=[MinLengthValidator(1, message="El nombre no puede estar vacío")]
    )
    avatar = models.CharField(max_length=255, default='/profiles/Profile1.png')
    background = models.CharField(max_length=500, default='')
    color = models.CharField(max_length=7, default='#000000')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} - {self.name}'
