from articles.models import Article
from django.core.management.base import BaseCommand
from search.search_indexes import ArticleDocument, index


class Command(BaseCommand):
    help = "Rebuild Elasticsearch index for articles"

    def handle(self, *args, **kwargs):
        # 인덱스 삭제
        index.delete(ignore=404)
        self.stdout.write(self.style.WARNING("Deleted the index"))

        # 인덱스 생성
        ArticleDocument.init()
        self.stdout.write(self.style.SUCCESS("Created the index"))

        # 데이터 재인덱싱
        for article in Article.objects.all():
            doc = ArticleDocument.from_django(article)
            doc.save()
        self.stdout.write(self.style.SUCCESS("Reindexed all articles"))
