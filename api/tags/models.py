from django.db import models


class Tag(models.Model):
    TAG_CHOICES = [
        (0, "전체"),
        (1, "일상"),
        (2, "연애 훈수"),
        (3, "집안일 훈수"),
        (4, "고민 훈수"),
        (5, "소소 훈수"),
        (6, "상상 훈수"),
        (7, "패션 훈수"),
        (8, "게임"),
        (9, "모바일 게임 훈수"),
        (10, "PC 게임 훈수"),
        (11, "교육 훈수"),
    ]

    tag_id = models.IntegerField(choices=TAG_CHOICES, unique=True, primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
