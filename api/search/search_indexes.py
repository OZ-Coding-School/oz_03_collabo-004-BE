from articles.models import Article
from elasticsearch_dsl import Date, Document, Index, Integer, Text, analyzer, tokenizer
from elasticsearch_dsl.connections import connections

connections.create_connection(hosts=["http://elasticsearch:9200"])

korean_analyzer = analyzer(
    "korean_analyzer",
    tokenizer=tokenizer("nori_tokenizer"),
    filter=["lowercase", "nori_part_of_speech", "nori_readingform"],
)


class ArticleDocument(Document):
    title = Text(analyzer=korean_analyzer)
    content = Text(analyzer=korean_analyzer)
    created_at = Date()

    class Index:
        name = "articles"

    @classmethod
    def from_django(cls, article):
        return cls(
            meta={"id": article.id},
            title=article.title,
            content=article.content,
            created_at=article.created_at,
        )


# Create the index with the custom settings
index = Index(ArticleDocument.Index.name)
index.settings(number_of_shards=1, number_of_replicas=0)
index.analyzer(korean_analyzer)
index.create()
