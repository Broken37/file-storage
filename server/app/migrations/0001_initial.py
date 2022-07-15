# Generated by Django 4.0.6 on 2022-07-15 14:43

from django.db import migrations, models
import filesystem.crypto


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(default=filesystem.crypto.get_random_string, max_length=32, unique=True)),
                ('data', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=32)),
                ('last_name', models.CharField(max_length=32)),
                ('user_name', models.CharField(max_length=32, unique=True)),
                ('password', models.CharField(max_length=128)),
                ('root_key', models.CharField(max_length=32)),
            ],
        ),
    ]
