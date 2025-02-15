from locust import HttpUser, task, constant, between
import json

# после первого старта и инита пользователей, необходимо задать им большие балансы в БД
# UPDATE shop."balance" SET amount = 461168601842738
# WHERE id IN (
#     SELECT balance_id FROM shop."user" WHERE username IN ('testuser1', 'testuser2')
# );

class ApiTest(HttpUser):
    wait_time = constant(1)  # Пауза между запросами 1 секунда

    # Переменные для хранения токенов
    token1 = ""
    token2 = ""

    def on_start(self):
        """Этот метод выполняется перед началом выполнения задач."""
        self.authenticate()

    def authenticate(self):
        """Аутентификация пользователей и получение токенов."""
        # Логин и получение JWT-токена для первого пользователя
        response = self.client.post("/api/auth", json={
            "username": "testuser1",
            "password": "Password123@"
        })
        
        if response.status_code == 200:
            self.token1 = response.json().get("token")
            # print("Authenticated testuser1 successfully.")
        else:
            print(f"Authentication failed for testuser1: {response.text}")

        # Логин и получение JWT-токена для второго пользователя
        response = self.client.post("/api/auth", json={
            "username": "testuser2",
            "password": "Password123@"
        })
        
        if response.status_code == 200:
            self.token2 = response.json().get("token")
            # print("Authenticated testuser2 successfully.")
        else:
            print(f"Authentication failed for testuser2: {response.text}")
        
    @task(3)
    def get_info(self):
        """Запрос информации о монетах для первого пользователя."""
        if self.token1:
            self.client.get("/api/info", headers={"Authorization": f"Bearer {self.token1}"})
    
    @task(2)
    def send_coin(self):
        """Отправка монет от первого пользователя ко второму."""
        if self.token1:
            self.client.post("/api/sendCoin", json={
                "toUser": "testuser2",
                "amount": 1
            }, headers={"Authorization": f"Bearer {self.token1}"})
    
    @task(1)
    def buy_item(self):
        """Покупка предмета для второго пользователя."""
        if self.token2:
            self.client.get("/api/buy/pen", headers={"Authorization": f"Bearer {self.token2}"})

# Конфигурация для отчетности в формате HTML
if __name__ == "__main__":
    import os
    # Мы получаем значения total_users и max_rps из командной строки
    total_users = 100000
    max_rps = 5
    os.system(f"locust -f locustfile.py --host=http://localhost:8080 --headless -u {total_users} -r {max_rps} --run-time 5m --html report.html")
