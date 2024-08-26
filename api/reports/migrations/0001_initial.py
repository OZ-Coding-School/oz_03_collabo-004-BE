# Generated by Django 5.1 on 2024-08-26 12:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('articles', '0004_remove_article_like_count_article_likes'),
        ('comments', '0002_remove_commentimage_image_url_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_detail', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('PD', '대기 중'), ('IP', '처리 중'), ('RS', '처리 완료'), ('RJ', '거부됨')], default='PD', max_length=2)),
                ('reported_article', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='articles.article')),
                ('reported_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports_against_user', to=settings.AUTH_USER_MODEL)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_articles', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CommentReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('report_detail', models.CharField(max_length=255)),
                ('status', models.CharField(choices=[('PD', '대기 중'), ('IP', '처리 중'), ('RS', '처리 완료'), ('RJ', '거부됨')], default='PD', max_length=2)),
                ('reported_comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='comments.comment')),
                ('reported_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_against_user', to=settings.AUTH_USER_MODEL)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported_comments', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]