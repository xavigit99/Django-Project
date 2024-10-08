# Generated by Django 5.1.1 on 2024-10-04 10:25

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0006_feedback'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='post',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='user',
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('category', models.CharField(choices=[('Meat', 'Meat'), ('Fish', 'Fish'), ('Vegetarian', 'Vegetarian'), ('Healthy', 'Healthy')], max_length=20)),
                ('ingredients', models.TextField()),
                ('time', models.IntegerField()),
                ('image', models.ImageField(blank=True, null=True, upload_to='recipes/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='FavouritePost',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
    ]
