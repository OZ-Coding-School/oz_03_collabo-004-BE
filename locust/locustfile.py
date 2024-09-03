from locust import HttpUser, between, task


class Quickstart(HttpUser):
    wait_time = between(1, 2)

    @task(1)
    def ping_pong(self):
        self.client.get("/ping")
