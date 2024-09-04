import random
import string

from locust import HttpUser, between, task


class WebsiteUser(HttpUser):
    wait_time = between(1, 5)

    def on_start(self):
        self.username = self.generate_random_username()
        self.password = "password123"
        self.nickname = self.generate_random_nickname()
        self.email = f"{self.username}@example.com"
        self.cookies = None

        self.register()
        self.login()

        self.article_id = None
        self.create_article()

    def generate_random_username(self):
        return "user_" + "".join(random.choices(string.ascii_letters, k=8))

    def generate_random_nickname(self):
        return "nickname_" + "".join(random.choices(string.ascii_letters, k=8))

    def generate_random_tags(self):
        """태그를 최대 3개까지 랜덤으로 선택"""
        available_tags = [
            {"tag_id": 2, "name": "연애 훈수"},
            {"tag_id": 3, "name": "집안일 훈수"},
            {"tag_id": 4, "name": "고민 훈수"},
            {"tag_id": 5, "name": "소소 훈수"},
            {"tag_id": 6, "name": "상상 훈수"},
            {"tag_id": 7, "name": "패션 훈수"},
            {"tag_id": 9, "name": "모바일 게임 훈수"},
            {"tag_id": 10, "name": "PC 게임 훈수"},
            {"tag_id": 11, "name": "교육 훈수"},
        ]

        selected_tags = random.sample(available_tags, k=random.randint(0, 3))
        return selected_tags

    def register(self):
        """회원가입을 수행합니다."""
        response = self.client.post(
            "/api/auth/register/",
            json={
                "username": self.username,
                "password": self.password,
                "nickname": self.nickname,
                "email": self.email,
            },
        )
        if response.status_code == 201:
            print(f"User {self.username} registered successfully.")
        else:
            print(
                f"Failed to register user {self.username}. Status code: {response.status_code}"
            )

    def login(self):
        """로그인을 수행하고 쿠키를 저장합니다."""
        response = self.client.post(
            "/api/auth/login/",
            json={"username": self.username, "password": self.password},
        )
        if response.status_code == 200:
            self.cookies = response.cookies
            print(f"User {self.username} logged in successfully.")
        else:
            self.cookies = None  # 로그인 실패 시 쿠키를 None으로 설정
            print(
                f"Failed to log in user {self.username}. Status code: {response.status_code}"
            )

    @task
    def view_profile(self):
        """프로필 조회 요청을 보냅니다."""
        if self.cookies:
            response = self.client.get("/api/account/profile/", cookies=self.cookies)
            if response.status_code == 200:
                print(f"User {self.username} profile viewed successfully.")
            else:
                print(
                    f"Failed to view profile for {self.username}. Status code: {response.status_code}"
                )

    @task
    def update_profile(self):
        """프로필 수정 요청을 보냅니다."""
        if self.cookies:
            updated_nickname = self.generate_random_nickname()
            selected_tags = self.generate_random_tags()
            response = self.client.put(
                "/api/account/profile/update/",
                json={
                    "nickname": updated_nickname,
                    "bio": "This is my updated bio",
                    "selected_tags": selected_tags,
                },
                cookies=self.cookies,
            )
            if response.status_code == 200:
                print(f"User {self.username} profile updated successfully.")
            else:
                print(
                    f"Failed to update profile for {self.username}. Status code: {response.status_code}"
                )

    @task
    def create_article(self):
        """게시글을 작성합니다."""
        if self.cookies:

            valid_tag_ids = [2, 3, 4, 5, 6, 7, 9, 10, 11]
            tag_id = random.choice(valid_tag_ids)

            response = self.client.post(
                "/api/article/create/",
                json={
                    "title": "Test Article",
                    "content": "This is a test article created by Locust.",
                    "tag_id": tag_id,  # 1~11 태그 중 랜덤 선택
                },
                cookies=self.cookies,
            )
            if response.status_code == 201:
                self.article_id = response.json().get("article_id")
                print(f"Article {self.article_id} created successfully.")
            else:
                print(f"Failed to create article. Status code: {response.status_code}")

    @task
    def like_article(self):
        """게시글에 좋아요를 누르거나 취소합니다."""
        if self.article_id and self.cookies:
            response = self.client.post(
                f"/api/article/{self.article_id}/like/", cookies=self.cookies
            )
            if response.status_code == 200:
                print(f"Article {self.article_id} like toggled successfully.")
            else:
                print(f"Failed to toggle like. Status code: {response.status_code}")

    @task
    def view_article(self):
        """게시글 조회수 증가를 테스트합니다."""
        if self.article_id:
            response = self.client.get(f"/api/article/{self.article_id}/view/")
            if response.status_code == 200:
                print(f"Article {self.article_id} viewed successfully.")
            else:
                print(f"Failed to view article. Status code: {response.status_code}")

    @task
    def update_article(self):
        """게시글을 수정합니다."""
        if self.article_id and self.cookies:

            valid_tag_ids = [2, 3, 4, 5, 6, 7, 9, 10, 11]
            tag_id = random.choice(valid_tag_ids)

            response = self.client.put(
                f"/api/article/update/{self.article_id}/",
                json={
                    "title": "Updated Title",
                    "content": "Updated content.",
                    "tag_id": tag_id,
                },
                cookies=self.cookies,
            )
            if response.status_code == 200:
                print(f"Article {self.article_id} updated successfully.")
            else:
                print(f"Failed to update article. Status code: {response.status_code}")

    @task
    def delete_article(self):
        """게시글을 삭제합니다."""
        if self.article_id and self.cookies:
            response = self.client.delete(
                f"/api/article/delete/{self.article_id}/", cookies=self.cookies
            )
            if response.status_code == 204:
                print(f"Article {self.article_id} deleted successfully.")
                self.article_id = None  # 게시글 삭제 후 article_id 초기화
            else:
                print(f"Failed to delete article. Status code: {response.status_code}")

    @task
    def report_article(self):
        """게시글 신고 요청을 보냅니다."""
        if self.article_id and self.cookies:
            response = self.client.post(
                "/api/report/article/{self.article_id}/",
                json={
                    "report_detail": "spam or inappropriate content",
                },
                cookies=self.cookies,
            )
            if response.status_code == 200:
                print(f"Article {self.article} reported successfully.")
            else:
                print(
                    f"Failed to report article for {self.article}. Status code: {response.status_code}"
                )

    @task
    def report_comment(self):
        """댓글 신고 요청을 보냅니다."""
        if self.comment_id and self.cookies:
            response = self.client.post(
                "/api/report/comment/{comment_id}/",
                json={
                    "report_detail": "spam or inappropriate content",
                },
                cookies=self.cookies,
            )
            if response.status_code == 200:
                print(f"Comment {self.comment} reported successfully.")
            else:
                print(
                    f"Failed to report comment for {self.comment}. Status code: {response.status_code}"
                )

    @task
    def get_ai_hunsoo(self):
        """ai 답변 조회 요청을 보냅니다."""
        article_id = self.article_id
        response = self.client.get(
            "/api/ai_hunsu/{article_id}",
            cookies=self.cookies,
        )
        if response.status_code == 200:
            print(f"Ai_hunsoo for {self.article} gotten successfully.")
        else:
            print(
                f"Failed to get ai_hunsoo for {self.article}. Status code: {response.status_code}"
            )
