import random
import string
from locust import HttpUser, between, task, events

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

        if self.cookies:
            self.article_id = None
            self.comment_id = None
            self.create_article()

            if self.article_id:
                self.create_comment()
            else:
                print("Article creation failed, skipping comment creation.")

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
        with self.client.post(
            "/api/auth/register/",
            json={
                "username": self.username,
                "password": self.password,
                "nickname": self.nickname,
                "email": self.email,
            },
            catch_response=True
        ) as response:
            if response.status_code == 201:
                events.request_success.fire(
                    request_type="POST",
                    name="/api/auth/register/",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=len(response.content),
                )
            else:
                events.request_failure.fire(
                    request_type="POST",
                    name="/api/auth/register/",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=len(response.content),
                    exception=Exception(f"Failed to register user: {response.status_code}")
                )

    def login(self):
        """로그인을 수행하고 쿠키를 저장합니다."""
        with self.client.post(
            "/api/auth/login/",
            json={"username": self.username, "password": self.password},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                self.cookies = response.cookies
                events.request_success.fire(
                    request_type="POST",
                    name="/api/auth/login/",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=len(response.content),
                )
            else:
                self.cookies = None
                events.request_failure.fire(
                    request_type="POST",
                    name="/api/auth/login/",
                    response_time=response.elapsed.total_seconds() * 1000,
                    response_length=len(response.content),
                    exception=Exception(f"Failed to log in user: {response.status_code}")
                )
                self.environment.runner.quit()

    @task
    def view_profile(self):
        """프로필 조회 요청을 보냅니다."""
        if self.cookies:
            with self.client.get("/api/account/profile/", cookies=self.cookies, catch_response=True) as response:
                if response.status_code == 200:
                    events.request_success.fire(
                        request_type="GET",
                        name="/api/account/profile/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="GET",
                        name="/api/account/profile/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to view profile: {response.status_code}")
                    )

    @task
    def update_profile(self):
        """프로필 수정 요청을 보냅니다."""
        if self.cookies:
            updated_nickname = self.generate_random_nickname()
            selected_tags = self.generate_random_tags()
            with self.client.put(
                "/api/account/profile/update/",
                json={
                    "nickname": updated_nickname,
                    "bio": "This is my updated bio",
                    "selected_tags": selected_tags,
                },
                cookies=self.cookies,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    events.request_success.fire(
                        request_type="PUT",
                        name="/api/account/profile/update/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="PUT",
                        name="/api/account/profile/update/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to update profile: {response.status_code}")
                    )

    @task
    def create_article(self):
        """게시글을 작성합니다."""
        if self.cookies:
            valid_tag_ids = [2, 3, 4, 5, 6, 7, 9, 10, 11]
            tag_id = random.choice(valid_tag_ids)

            with self.client.post(
                "/api/article/create/",
                json={
                    "title": "Test Article",
                    "content": "This is a test article created by Locust.",
                    "tag_id": tag_id,
                },
                cookies=self.cookies,
                catch_response=True
            ) as response:
                if response.status_code == 201:
                    self.article_id = response.json().get("article_id")
                    events.request_success.fire(
                        request_type="POST",
                        name="/api/article/create/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="POST",
                        name="/api/article/create/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to create article: {response.status_code}")
                    )

    @task
    def update_article(self):
        """게시글을 수정합니다."""
        if self.article_id and self.cookies:
            valid_tag_ids = [2, 3, 4, 5, 6, 7, 9, 10, 11]
            tag_id = random.choice(valid_tag_ids)

            with self.client.put(
                f"/api/article/update/{self.article_id}/",
                json={
                    "title": "Updated Title",
                    "content": "Updated content.",
                    "tag_id": tag_id,
                },
                cookies=self.cookies,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    events.request_success.fire(
                        request_type="PUT",
                        name=f"/api/article/update/{self.article_id}/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="PUT",
                        name=f"/api/article/update/{self.article_id}/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to update article: {response.status_code}")
                    )

    @task
    def create_comment(self):
        """게시글에 댓글을 작성합니다."""
        if self.article_id and self.cookies:
            article_response = self.client.get(f"/api/article/{self.article_id}/", cookies=self.cookies)
            if article_response.status_code == 200:
                article_author = article_response.json().get("author")
                if article_author == self.username:
                    print(f"User {self.username} cannot comment on their own article.")
                    return  # 자신의 게시글에 댓글을 작성하지 않음

            with self.client.post(
                f"/comments/create/articles/{self.article_id}/",
                json={"content": "This is a test comment created by Locust."},
                cookies=self.cookies,
                catch_response=True
            ) as response:
                if response.status_code == 201:
                    self.comment_id = response.json().get("id")
                    events.request_success.fire(
                        request_type="POST",
                        name=f"/comments/create/articles/{self.article_id}/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="POST",
                        name=f"/comments/create/articles/{self.article_id}/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to create comment: {response.status_code}")
                    )

    @task
    def react_to_comment(self):
        """댓글에 도움이 돼요/안 돼요 반응을 추가하거나 삭제합니다."""
        if self.comment_id and self.cookies:
            article_response = self.client.get(f"/api/article/{self.article_id}/", cookies=self.cookies)
            if article_response.status_code == 200:
                article_author = article_response.json().get("author")
                if article_author == self.username:
                    print(f"User {self.username} cannot react to their own comment.")
                    return

            reaction_type = random.choice(["helpful", "not_helpful"])
            with self.client.post(
                f"/comments/{self.comment_id}/react/",
                json={"reaction_type": reaction_type},
                cookies=self.cookies,
                catch_response=True
            ) as response:
                if response.status_code in [200, 201]:
                    events.request_success.fire(
                        request_type="POST",
                        name=f"/comments/{self.comment_id}/react/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="POST",
                        name=f"/comments/{self.comment_id}/react/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to react to comment: {response.status_code}")
                    )

    @task
    def like_article(self):
        """게시글에 좋아요를 누르거나 취소합니다."""
        if self.article_id and self.cookies:
            article_response = self.client.get(f"/api/article/{self.article_id}/", cookies=self.cookies)
            if article_response.status_code == 200:
                article_author = article_response.json().get("author")
                if article_author == self.username:
                    print(f"User {self.username} cannot like their own article.")
                    return

            with self.client.post(f"/api/article/{self.article_id}/like/", cookies=self.cookies, catch_response=True) as response:
                if response.status_code == 200:
                    events.request_success.fire(
                        request_type="POST",
                        name=f"/api/article/{self.article_id}/like/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="POST",
                        name=f"/api/article/{self.article_id}/like/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to like article: {response.status_code}")
                    )

    @task
    def view_article(self):
        """게시글 조회수 증가를 테스트합니다."""
        if self.article_id:
            with self.client.get(f"/api/article/{self.article_id}/view/", catch_response=True) as response:
                if response.status_code == 200:
                    events.request_success.fire(
                        request_type="GET",
                        name=f"/api/article/{self.article_id}/view/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="GET",
                        name=f"/api/article/{self.article_id}/view/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to view article: {response.status_code}")
                    )

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
                "/api/report/comment/{self.comment_id}/",
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
        if self.article_id:
            response = self.client.get(
                "/api/ai_hunsu/{self.article_id}",
            )
            if response.status_code == 200:
                print(f"Ai_hunsoo for {self.article} gotten successfully.")
            else:
                print(
                    f"Failed to get ai_hunsoo for {self.article}. Status code: {response.status_code}"
                )

    @task
    def list_notifications(self):
        """알림 목록을 조회하고 첫 번째 알림의 ID를 저장합니다."""
        if self.cookies:
            with self.client.get("/api/notification/", cookies=self.cookies, catch_response=True) as response:
                if response.status_code == 200:
                    notifications = response.json()
                    if notifications:
                        self.notification_id = notifications[0]['id']
                    events.request_success.fire(
                        request_type="GET",
                        name="/api/notification/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="GET",
                        name="/api/notification/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to retrieve notifications: {response.status_code}")
                    )

    @task
    def mark_notification_as_read(self):
        """저장된 notification_id로 알림을 읽음 상태로 변경합니다."""
        if self.cookies and self.notification_id:
            with self.client.post(
                f"/api/notification/{self.notification_id}/read/",
                cookies=self.cookies,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    events.request_success.fire(
                        request_type="POST",
                        name=f"/api/notification/{self.notification_id}/read/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="POST",
                        name=f"/api/notification/{self.notification_id}/read/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to mark notification as read: {response.status_code}")
                    )

    @task
    def delete_notification(self):
        """저장된 notification_id로 알림을 삭제합니다."""
        if self.cookies and self.notification_id:
            with self.client.delete(
                f"/api/notification/{self.notification_id}/delete/",
                cookies=self.cookies,
                catch_response=True
            ) as response:
                if response.status_code == 204:
                    events.request_success.fire(
                        request_type="DELETE",
                        name=f"/api/notification/{self.notification_id}/delete/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="DELETE",
                        name=f"/api/notification/{self.notification_id}/delete/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to delete notification: {response.status_code}")
                    )

    @task
    def delete_article(self):
        """게시글을 삭제합니다."""
        if self.article_id and self.cookies:
            with self.client.delete(f"/api/article/delete/{self.article_id}/", cookies=self.cookies, catch_response=True) as response:
                if response.status_code == 204:
                    self.article_id = None  # 게시글 삭제 후 article_id 초기화
                    events.request_success.fire(
                        request_type="DELETE",
                        name=f"/api/article/delete/{self.article_id}/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                    )
                else:
                    events.request_failure.fire(
                        request_type="DELETE",
                        name=f"/api/article/delete/{self.article_id}/",
                        response_time=response.elapsed.total_seconds() * 1000,
                        response_length=len(response.content),
                        exception=Exception(f"Failed to delete article: {response.status_code}")
                    )



