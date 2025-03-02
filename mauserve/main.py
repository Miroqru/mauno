"""Главный файл сервера.

Производит полную настройку и подключение всех компонентов.
В том числе настраивает подключение базы данных и всех обработчиков.
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from tortoise import generate_config
from tortoise.contrib.fastapi import RegisterTortoise

# Подгружаем роутеры
from mauserve.config import config
from mauserve.routers import ROUTERS

# Жизненный цикл базы данных
# ==========================

DB_CONFIG = generate_config(
    str(config.db_url),
    app_modules={"models": ["mauserve.models"]},
    testing=config.debug,
    connection_label="models",
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Жизненный цикл базы данных.

    Если это тестовая сессия, то создаёт базу данных в оперативной
    памяти.
    Иначе же просто  к базе данных postgres, на всё время
    работы сервера.
    """
    async with RegisterTortoise(
        app=app,
        config=DB_CONFIG,
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
    version="v0.4",
    root_path="/api",
)

origins = [
    "*",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Подключает сторонние роутеры
for router in ROUTERS:
    app.include_router(router)
    logger.info("Include router: {}", router.prefix)
