# Generated by Django 5.1 on 2024-08-22 05:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_remove_articleimage_image_url_article_tags_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articleimage',
            name='article',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='articles.article'),
        ),
    ]