# Generated by Django 4.0.6 on 2022-07-24 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='data',
            field=models.TextField(null=True),
        ),
    ]