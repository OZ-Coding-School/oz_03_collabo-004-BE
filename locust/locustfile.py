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

    def generate_random_username(self):
        return "user_" + "".join(random.choices(string.ascii_letters, k=8))

    def generate_random_nickname(self):
        return "nickname_" + "".join(random.choices(string.ascii_letters, k=8))

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
            response = self.client.put(
                "/api/account/profile/update/",
                json={
                    "nickname": updated_nickname,
                    "bio": "This is my updated bio",
                },
                cookies=self.cookies,
            )
            if response.status_code == 200:
                print(f"User {self.username} profile updated successfully.")
            else:
                print(
                    f"Failed to update profile for {self.username}. Status code: {response.status_code}"
                )
