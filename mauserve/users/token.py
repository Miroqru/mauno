"""JWT валидартор.

Простой набор методов для валидации токенов пользователей.
Токены используются для подтверждения пользователя.
"""

from datetime import datetime

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mauserve.models import UserModel

bearer = HTTPBearer()


class SimpleTokenManager:
    """Простой класс для упрощения процесс работы с токенами.

    Позволяет создавать и управлять JWT токенами для проверки
    подлинности пользователя.

    :param secret_key: Секретный ключ для создания токенов.
    :type secret_key: str
    :param ttl: Сколько будет жить каждый токен. (в минутах)
    :type ttl: int
    """

    def __init__(self, secret_key: str, ttl: int) -> None:
        self._secret_key = secret_key
        self._ttl = ttl

    def new_token(self, user: UserModel) -> str:
        """Создаёт новый токен, привязанный к пользователю.

        Теперь вы сможете использовать этот токен вместо пароля.
        В токен добавляются ID пользователя, для которого он был создан,
        а также срок жизни.

        :param user: Данные пользователя.
        :type user: UserModel
        :returns: новый токен для пользователя.
        :rtype: str
        """
        now = int(datetime.now().timestamp())
        return jwt.encode(
            {
                "username": user.username,
                "created": now,
                "expired": now + self._ttl * 60,
            },
            self._secret_key,
            algorithm="HS256",
        )

    async def read_token(
        self, cred: HTTPAuthorizationCredentials = Depends(bearer)
    ) -> UserModel:
        """Извлекает пользователя из токена.

        Проверяет что введённый токен корректный, ещё живой и что
        указанный пользователь ещё существует.
        Если всё прошло хорошо - вернёт экземпляр пользователя из
        базы данных.
        Иначе вернёт исключение.

        :param cred: Данные пользователя для авторизации из заголовка.
        :type cred: HTTPAuthorizationCredentials
        :return: Пользователь, связанный с токеном.
        :rtype: UserModel
        """
        try:
            payload = jwt.decode(
                cred.credentials, self._secret_key, algorithms="HS256"
            )
        except Exception:
            raise HTTPException(401, "Invalid token")

        if payload.get("expired") < int(datetime.now().timestamp()):
            raise HTTPException(401, "Token has expired")

        user = await UserModel.get_or_none(username=payload.get("username"))
        if user is None:
            raise HTTPException(401, "Invalid user id")

        return user
