# Generated by Django 5.1 on 2024-08-26 09:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comments', '0002_remove_commentimage_image_url_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='commentimage',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='commentreaction',
            name='deleted_at',
            field=models.DateTimeField(null=True),
        ),
    ]