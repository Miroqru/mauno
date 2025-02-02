"""Главный файл сервера.

Производит полную настройку и подключение всех компонентов.
В том числе настраивает подключение базы данных и всех обработчиков.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

# Подгружаем роутеры
from tortoise import generate_config
from tortoise.contrib.fastapi import RegisterTortoise

# from mauserve.users.router import router as user_router
from mauserve.config import config

# Жизненный цикл базы данных
# ==========================


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Жизненный цикл базы данных.

    Если это тестовая сессия, то создаёт базу данных в оперативной
    памяти.
    Иначе же просто  к базе данных postgres, на всё время
    работы сервера.
    """
    if config.debug:
        db_config = generate_config(
            config.test_db_url,
            app_modules={"models": ["mauserve.models"]},
            testing=True,
            connection_label="models",
        )
    else:
        db_config = generate_config(
            config.db_url,
            app_modules={"models": ["mauserve.models"]},
            connection_label="models",
        )

    async with RegisterTortoise(
        app=app,
        config=db_config,
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        # db connected
        yield
        # app teardown

    # db connections closed
    # ? Тут мог бы быть более корректный код, но увы
    # if config.debug:
    #     await Tortoise._drop_databases()


# Константы
# =========

app = FastAPI(
    lifespan=lifespan,
    title="mauserve",
    debug=config.debug,
    version="v0.1",
    root_path="/api",
)

# Подключает сторонние роутеры
# app.include_router(user_router)
