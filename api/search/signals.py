from articles.models import Article
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from elasticsearch import NotFoundError

from .search_indexes import ArticleDocument


@receiver(post_save, sender=Article)
def index_article(sender, instance, **kwargs):
    article_doc = ArticleDocument.from_django(instance)
    article_doc.save()


@receiver(post_delete, sender=Article)
def delete_article_from_index(sender, instance, **kwargs):
    try:
        article_doc = ArticleDocument.get(id=instance.id)
        article_doc.delete()
    except NotFoundError:
        pass
