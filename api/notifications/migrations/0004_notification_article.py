# Generated by Django 5.1 on 2024-09-06 04:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_alter_articleimage_image'),
        ('notifications', '0003_remove_notification_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='article',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='articles.article'),
            preserve_default=False,
        ),
    ]