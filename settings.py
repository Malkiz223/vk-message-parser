import os

VK_LOGIN: str = os.getenv('VK_LOGIN')  # 'admin@gmail.com'
VK_PASSWORD: str = os.getenv('VK_PASSWORD')  # 'qwerty123'
TWO_FACTOR: bool = True  # False, если у вас отсутствует двухфакторная аутентификация

# Настройки PostgreSQL
postgres_user: str = 'postgres'  # пользователь по умолчанию
postgres_password: str = os.getenv('POSTGRESQL_PASSWORD')  # пароль для подключения к пользователю
postgres_dbname: str = 'vk_messages'  # название созданной вами базы
postgres_host: str = '127.0.0.1'  # localhost, ip по умолчанию
postgres_port: int = 5432  # порт по умолчанию
