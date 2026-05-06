# Generated migration to migrate WatchProgress from User to Profile

from django.db import migrations, models
import django.db.models.deletion


def migrate_watchprogress_to_profile(apps, schema_editor):
    """
    Migrar datos de WatchProgress de user a profile.
    Asigna el primer perfil de cada usuario a sus registros de progreso.
    """
    WatchProgress = apps.get_model('backoffice', 'WatchProgress')
    Profile = apps.get_model('manager', 'Profile')
    
    for progress in WatchProgress.objects.all():
        # Obtener el primer perfil del usuario
        first_profile = Profile.objects.filter(user=progress.user).first()
        
        if first_profile:
            progress.profile = first_profile
            progress.save()
        else:
            # Si no hay perfil, eliminar el progreso (no debería pasar)
            progress.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('backoffice', '0003_watchprogress'),
        ('manager', '0002_watchlist'),
    ]

    operations = [
        # Paso 1: Agregar campo profile como nullable
        migrations.AddField(
            model_name='watchprogress',
            name='profile',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='watch_progress',
                to='manager.profile'
            ),
        ),
        
        # Paso 2: Migrar datos de user a profile
        migrations.RunPython(migrate_watchprogress_to_profile, reverse_code=migrations.RunPython.noop),
        
        # Paso 3: Cambiar unique_together para quitar user, agregar profile
        migrations.AlterUniqueTogether(
            name='watchprogress',
            unique_together={('profile', 'anime')},
        ),
        
        # Paso 4: Hacer profile non-nullable
        migrations.AlterField(
            model_name='watchprogress',
            name='profile',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='watch_progress',
                to='manager.profile'
            ),
        ),
        
        # Paso 5: Eliminar campo user y cambiar related_name en anime
        migrations.RemoveField(
            model_name='watchprogress',
            name='user',
        ),
        
        migrations.AlterField(
            model_name='watchprogress',
            name='anime',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='profile_progress',
                to='backoffice.anime'
            ),
        ),
    ]
