# Generated by Django 5.1.2 on 2024-11-02 11:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipesapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recipe',
            name='recipe_image',
            field=models.ImageField(null=True, upload_to='media'),
        ),
    ]
