# Mau;engine

<img src="./docs/assets/logo.png" width="256"></img>

[![License](https://img.shields.io/badge/License-AGPL%20v3-red?style=flat&labelColor=%23B38B74&color=%23FF595F)](./LICENSE)
![Mau version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fcodeberg.org%2FSalormoon%2Fmauno%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml&query=project.version&prefix=v&style=flat&label=Mau&labelColor=%23B38B74&color=%2373FFAD)
![Python version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fcodeberg.org%2FSalormoon%2Fmauno%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml&query=project.requires-python&style=flat&logo=python&logoColor=%23B38B74&label=python&labelColor=%23805959&color=%232185A6)
[![Docs](https://img.shields.io/badge/docs-miroq-%2300cc99?style=flat&labelColor=%23805959&color=%2330BFB3&link=https%3A%2F%2Fmau.miroq.ru%2Fdocs%2F)](https://mau.miroq.ru/docs/)
![GitHub stars](https://img.shields.io/github/stars/miroqru/mauno?style=flat&logo=github&logoColor=%23E6D0A1&label=Stars&labelColor=%23805959&color=%23FFF766)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

**Mau** - игровой движок для *карточных игр*. Как например Uno, дурак, только с добавлением
множества дополнительных возможностей.
Цель проекта - расширить горизонты карточных игр.

## Семейство Mau
Для полноценной игры одного движка недостаточно, потому представляем вам все
доступные компоненты:

- [Mau;cards](https://github.com/miroqru/mau-cards):
  Сервер-генератор изображений игровых карт.
- [Mau;serve](https://github.con/miroqru/mauserver):
  Web сервер для игрового движка, дополняющий его новыми функциями.
- [Mauren](https://github.com/miroqru/mauren):
  Клиентская библиотека для взаимодействия с сервером Mau.
- [Mau;tg](https://github.con/miroqru/mau-tg):
  Telegram бот для совместной игры в Mau в групповых чатах.

## Компоненты
Вот что входит в движок Mau:

- Колода карт:
  - Поведение карт
  - Игровые карты
  - Колода карт
  - Шаблоны для сборки колоды
- Игровой процесс:
  - Игра
  - Менеджер игроков
  - Игрок
  - Игровые правила
  - Револьвер
- Обработчик событий
- Менеджер сессий
- Хранилище для игр и игроков

## Поддержка проекта
Мы будем очень рады, если вы **поддержите развитие проекта**.
Есть несколько способов как вы можете это сделать:

- Оставить **звёздочку** в репозитории.
- **Играть** вместе с друзьями в Mau.
- **Участвовать в бета-тестировании** новых функций.
- **Предлагать** свои собственные идеи.
- Сообщать о найденных багах или даже предлагать их решение.
- **Сделать** форк проекта.

> Подробности в [документации](https://mau.miroq.ru/docs/use/maintenance)

Нам бы очень хотелось создать **лучшего бота** для весёлой совместной игры с друзьями!

## Благодарности

в начале это был **форк** [Mau Mau bot](https://github.com/jh0ker/mau_mau_bot).
Большое спасибо этому проекту, без него не появилась бы Mau.

И после произошло *чуть-чуть **много** изменений*:
- Переписан на *aiogram*.
- Разделена *архитектура* на бота и движок.
- Добавлены новые *игровые режимы*.
- Система игровых событий.
- С нуля переработанный движок.
- Использование стратегий для карт.
- Генератор колоды.
