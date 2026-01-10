import bcrypt


def verify_password(plain_password: str, hashed_password: bytes) -> bool:
    """Проверить пароль."""
    # Кодируем введенный пароль в bytes и сравниваем с хешем
    return bcrypt.checkpw(plain_password.encode(), hashed_password)


def get_password_hash(password: str) -> bytes:
    """Получить хеш пароля."""
    # Генерируем случайную соль (автоматически определяет раунды)
    salt = bcrypt.gensalt()

    # Кодируем пароль в байты
    pwd_bytes: bytes = password.encode()

    # Создаем хеш пароля с солью
    return bcrypt.hashpw(pwd_bytes, salt)