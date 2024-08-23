from django.db import models


class Tag(models.Model):
    TAG_CHOICES = [
        (0, "연애 훈수"),
        (1, "집안일 훈수"),
        (2, "고민 훈수"),
        (3, "소소 훈수"),
        (4, "상상 훈수"),
        (5, "패션 훈수"),
        (6, "게임 훈수"),
        (7, "교육 훈수"),
    ]

    tag_id = models.IntegerField(choices=TAG_CHOICES, unique=True, primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
