# Generated by Django 5.1 on 2024-09-05 15:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_alter_articleimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='articleimage',
            name='article',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='articles.article'),
        ),
    ]
