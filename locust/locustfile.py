import random

from locust import HttpUser, between, task


class QuestionUser(HttpUser):
    wait_time = between(1, 5)  # 각 태스크 사이에 1-5초 대기

    def on_start(self):
        # 사용자 회원가입
        self.client.post(
            "/api/auth/register/",
            json={
                "username": "testuser",
                "email": "testuser@example.com",
                "password": "password123",
                "nickname": "UserNickname",
            },
        )

        self.client.post(
            "/api/auth/login/",
            json={
                "username": "testuser",
                "password": "password123",
            },
        )

    @task(3)
    def edit_profile(self):
        # 프로필 업데이트
        self.client.put(
            "/api/account/profile/update",
            json={
                {
                    "nickname": "NewNickname",
                    "bio": "Updated bio",
                    "selected_tags": [1, 3, 5],
                }
            },
        )

    @task(2)
    def create_article(self):
        # 게시글 작성
        product_id = random.randint(1, 100)  # 1부터 100 사이의 랜덤 상품 ID
        self.client.get(
            f"/api/article/create",
            json={
                {
                    "title": "Article Title",
                    "content": "Article content",
                    "tag_ids": [1, 5, 7],
                    "images": "",
                }
            },
        )

    @task(1)
    def profile_view(self):
        self.client.get("/api/accounts/profile/")
