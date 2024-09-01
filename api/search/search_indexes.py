from articles.models import Article
from elasticsearch_dsl import Date, Document, Index, Integer, Text, analyzer, tokenizer
from elasticsearch_dsl.connections import connections

# Elasticsearch 연결 설정
connections.create_connection(hosts=["http://elasticsearch:9200"])

# Korean Analyzer 정의
korean_analyzer = analyzer(
    "korean_analyzer",
    tokenizer="nori_tokenizer",
    filter=["lowercase", "nori_part_of_speech", "nori_readingform"],
)


# 인덱스 정의 및 설정
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


# 인덱스 생성 또는 업데이트
index = Index(ArticleDocument.Index.name)
index.settings(
    number_of_shards=1,
    number_of_replicas=0,
    analysis={
        "analyzer": {
            "korean_analyzer": {
                "type": "custom",
                "tokenizer": "nori_tokenizer",
                "filter": ["lowercase", "nori_part_of_speech", "nori_readingform"],
            }
        }
    },
)

# 매핑을 인덱스에 추가
index.document(ArticleDocument)

# 인덱스가 이미 존재하지 않는 경우에만 생성
if not index.exists():
    index.create()
