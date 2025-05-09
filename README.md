# Mau(bot)

<img src="./docs/assets/logo.png" width="256"></img>

[![License](https://img.shields.io/badge/License-AGPL%20v3-red?style=flat&labelColor=%23B38B74&color=%23FF595F)](./LICENSE)
![Mau version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fcodeberg.org%2FSalormoon%2Fmauno%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml&query=project.version&prefix=v&style=flat&label=Mau&labelColor=%23B38B74&color=%2373FFAD)
![Python version](https://img.shields.io/badge/dynamic/toml?url=https%3A%2F%2Fcodeberg.org%2FSalormoon%2Fmauno%2Fraw%2Fbranch%2Fmain%2Fpyproject.toml&query=project.requires-python&style=flat&logo=python&logoColor=%23B38B74&label=python&labelColor=%23805959&color=%232185A6)
![Docs](https://img.shields.io/badge/docs-miroq-%2300cc99?style=flat&labelColor=%23805959&color=%2330BFB3&link=https%3A%2F%2Fmau.miroq.ru%2Fdocs%2F)
![GitHub stars](https://img.shields.io/github/stars/miroqru/mauno?style=flat&logo=github&logoColor=%23E6D0A1&label=Stars&labelColor=%23805959&color=%23FFF766)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Хотите сыграть в UNO со *своими друзьями* в Telegram?
Mauno поможет вам весело провести время.

**Немного особенностей**:

- 🎮 **Легко** научиться играть.
- 🍓 Много необычных и весёлых **игровых правил**.
- ☕ **Лобби** для чата.
- 🌟 Несколько вариантов **колод**.
- 📝 **Журнал** игровых событий.
- 🪄 `Callback` кнопочки и `inline query` к вашим услугам.
- 🃏 Красивые карточки.

> Бот использует `inline query` клавиатуру для карт.
> Будьте готовы что после игры остаётся *море сообщений* в чате.
> Зато это же так весело!


## Начало игры
Если вы заинтересованы, то давайте же **сыграем вместе**!

**Поиграть с нами** можно здесь: [@mau_room](https://t.me/mau_room).

Вот ссылочка на официального бота: [@mili_maubot](https://t.me/mili_maubot).
Заодно можете подписаться на канал [Salormoon](https://t.me/mili_qlaster),
чтобы следить за обновлениями бота и прочими новостями проекта.

**Всё что нужно знать чтобы начать игру**:

1. **Добавляем** бота в чат с друзьями.
2. Вводим `/game` для создания **нового лобби**.
3. Когда все игроки присоединились, **нажимаем** начать. (`/start_game`)
4. Весело **играем** партию.
5. Ошалеваем от веселья в чате и количества сообщений.
6. Создаём ещё одну комнату и продолжаем веселиться.

> Ознакомиться с полным списком команд вы можете в *меню* бота.
> На самом деле основных команд не так уж и много.

## Игровые правила
Ранее мы упомянули о **различных игровых правилах**.
Так вот, каждое правило привносит какую-то свою механику.
На данный момент доступно *16 игровых правил*:

- 👑 Один победитель.
- **🌀 Побочный выброс**: На каждую карту 1 вы можете выбросить ещё одну карту.
- **💸 Авто пропуск**: Нет подходящей карты - пропускаю. Экономит время при дуэлях.
- **🤝 Обмен руками**: Каждый раз как кто-то выкидываете 2, он обменивается картами
  с другим игроком.
- **👋 Без обмена**: При выборе с кем обменяться картами появляется вариант выбрать себя.
- **🧭 Обмен телами**: Каждый раз как кто-то выкидывает 0, все игроки
  обмениваются картами по кругу.
- **🍷 Беру до последнего**: Нету подходящей карты? Бери пока не появится.
- **🔫 Рулетка**: Не желаете брать карты, тогда выстрелите из револьвера.
  Если повезёт, брать будет уже следующий игрок.
- **🎲 Общий револьвер**: Похожа на рулетку, только револьвер один на всех.
- **🃏 самоцвет**: Для карт выбора цвета и +4 цвет выбирается по кругу.
- **🎨 Случайный цвет**: Для карты выбора цвета и +4 цвет выбирается случайно.
- **🎨 Какой цвет дальше**: На самом деле ваши карты совсем другого цвета.

> Будьте осторожным при выборе режимов, может случится так что игра превратится
> в **полный хаос**.
> Тогда всегда можно добавить *общий револьвер* для большего азарта.
> Ну или *один победитель*, чтобы не затягивать игру.

Если у вас есть **свои предложения** для игровых режимов, мы только рады будем их услышать.

## Локальная установка
Разумеется благодаря открытому коду вы можете запустить **своего бота**.
Или быть может *сделать форк* с добавлением новых функций?

Чтобы **развернуть локального бота**:

Для работы с зависимостями и виртуальным окружением используется
[uv](https://docs.astral.sh/uv/).

1. Клонируем репозиторий:

```sh
git clone https://github.com/miroqru/mauno
```

2. Устанавливаем зависимости (виртуальное окружение будет создано автоматически):

```sh
uv sync
```

3. Копируем файл с настройками `.env.dist` в `.env`.
4. Вставляем в файл токен от бота и путь к набору стикеров.
4. Запускаем бота:

```sh
uv run -m maubot
```

Ах да, ещё вам потребуется включить `inline mode` для вашего бота и
обязательно выставить `inline feedback` на 100%.
Сделать это в [BotFather](https://t.me/BotFather).
Без этого, отправленные вами карты не будут обрабатываться ботом.

> Вот и всё :)

## Поддержка проекта
Мы будем очень рады, если вы **поддержите развитие проекта**.
Есть несколько способов как вы можете это сделать:

- Оставить **звёздочку** в репозитории.
- **Играть** вместе с друзьями в Uno.
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
