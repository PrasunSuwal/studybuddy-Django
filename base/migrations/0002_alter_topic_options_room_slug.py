# Generated by Django 5.0.4 on 2024-06-19 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='topic',
            options={'ordering': ['-id']},
        ),
        migrations.AddField(
            model_name='room',
            name='slug',
            field=models.SlugField(default=''),
        ),
    ]
