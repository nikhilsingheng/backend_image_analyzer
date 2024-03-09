# Generated by Django 5.0.3 on 2024-03-06 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('image', '0003_alter_uploadedimage_pix'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='uploadedimage',
            name='pix',
        ),
        migrations.AddField(
            model_name='uploadedimage',
            name='image_height_flag',
            field=models.BooleanField(blank=True, default=False),
        ),
    ]