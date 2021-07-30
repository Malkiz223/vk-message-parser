import os

VK_LOGIN: str = os.getenv('VK_LOGIN')  # 'admin@gmail.com'
VK_PASSWORD: str = os.getenv('VK_PASSWORD')  # 'qwerty123'
TWO_FACTOR: bool = True  # False, если у вас отсутствует двухфакторная аутентификация

# Настройки PostgreSQL, если он есть
postgres_user: str = 'postgres'
postgres_password: str = os.getenv('POSTGRESQL_PASSWORD')
postgres_database: str = 'vk_messages'
postgres_host: str = '127.0.0.1'
postgres_port: int = 5432
