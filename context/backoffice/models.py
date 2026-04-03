from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class Anime(models.Model):
    title = models.CharField(max_length=255)
    year = models.IntegerField(
        validators=[
            MinValueValidator(1900, message="El año no puede ser anterior a 1900"),
            MaxValueValidator(datetime.now().year + 5, message="El año no puede ser tan futuro")
        ]
    )
    genre = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.URLField(max_length=500, blank=True)
    background_image = models.URLField(max_length=500, blank=True)
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=0.0,
        validators=[
            MinValueValidator(0.0, message="La calificación no puede ser negativa"),
            MaxValueValidator(10.0, message="La calificación no puede ser mayor a 10.0")
        ]
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.year})'


class Episode(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='episodes')
    episode_number = models.IntegerField(
        validators=[MinValueValidator(1, message="El número de episodio debe ser mayor a 0")]
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    duration = models.IntegerField(
        help_text='Duración en minutos',
        validators=[
            MinValueValidator(1, message="La duración debe ser al menos 1 minuto"),
            MaxValueValidator(300, message="La duración no puede exceder 300 minutos")
        ]
    )
    video_url = models.URLField(max_length=500, blank=True)
    thumbnail = models.URLField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['episode_number']
        unique_together = ['anime', 'episode_number']

    def __str__(self):
        return f'{self.anime.title} - Episodio {self.episode_number}'
