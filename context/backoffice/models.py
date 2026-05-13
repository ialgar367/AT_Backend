from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import datetime


class Anime(models.Model):
    AUDIO_CHOICES = [
        ('SUB', 'Subtitulado'),
        ('DUB', 'Doblado'),
        ('BOTH', 'Sub y Dub'),
    ]
    
    AGE_RATING_CHOICES = [
        ('TV-Y', 'TV-Y'),
        ('TV-PG', 'TV-PG'),
        ('TV-14', 'TV-14'),
        ('TV-MA', 'TV-MA'),
        ('R', 'R'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('SERIE', 'Serie'),
        ('PELÍCULA', 'Película'),
        ('OVA', 'OVA'),
        ('ESPECIAL', 'Especial'),
    ]
    
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
    audio_type = models.CharField(max_length=10, choices=AUDIO_CHOICES, default='SUB')
    age_rating = models.CharField(max_length=10, choices=AGE_RATING_CHOICES, default='TV-14')
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='SERIE')
    is_simulcast = models.BooleanField(default=False)
    episode_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    anime_slug = models.CharField(
        max_length=255, 
        blank=True, 
        help_text='Slug para búsqueda en GogoAnime (ej: one-piece, naruto-shippuden)'
    )
    
    likes = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    dislikes = models.IntegerField(default=0, validators=[MinValueValidator(0)])
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


class WatchProgress(models.Model):
    """
    Modelo para rastrear el progreso de visualización de un perfil en un anime
    """
    profile = models.ForeignKey('manager.Profile', on_delete=models.CASCADE, related_name='watch_progress')
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='profile_progress')
    current_episode = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Último episodio visto completamente"
    )
    watched = models.BooleanField(
        default=False,
        help_text="True si el usuario completó toda la serie"
    )
    last_watched = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['profile', 'anime']
        ordering = ['-last_watched']
        verbose_name = 'Watch Progress'
        verbose_name_plural = 'Watch Progress'

    def __str__(self):
        return f"{self.profile.name} - {self.anime.title} (Ep. {self.current_episode})"

