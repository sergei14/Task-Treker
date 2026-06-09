"""
token_parser.py

Файл содержит вспомогательные функции для работы
с публичными токенами проекта:
- генерацию безопасного токена;
- очистку токена от случайных пробелов;
- проверку корректности формата токена;
- безопасное сравнение двух токенов.

Публичный токен будет использоваться для доступа
к странице проекта и форме отправки фидбеков.
"""

import re
import secrets

from app.core.config import settings


TOKEN_PATTERN = re.compile(r"^[A-Za-z0-9_-]+$")


def generate_public_token() -> str:
    return secrets.token_urlsafe(settings.token_length)


def normalize_public_token(token: str) -> str:
    return token.strip()


def is_valid_public_token(token: str) -> bool:
    normalized_token = normalize_public_token(token)

    if len(normalized_token) < settings.token_length:
        return False

    return bool(TOKEN_PATTERN.fullmatch(normalized_token))


def tokens_match(first_token: str, second_token: str) -> bool:
    normalized_first_token = normalize_public_token(first_token)
    normalized_second_token = normalize_public_token(second_token)

    if not normalized_first_token or not normalized_second_token:
        return False

    return secrets.compare_digest(
        normalized_first_token,
        normalized_second_token,
    )