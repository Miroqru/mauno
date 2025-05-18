# Локальная установка

Разумеется благодаря открытому коду вы можете запустить **своего бота**.
Или быть может *сделать форк* с добавлением новых функций?

Чтобы **развернуть локального бота**:

Для работы с зависимостями и виртуальным окружением используется
[uv](https://docs.astral.sh/uv/).

1. Клонируем репозиторий:

```sh
git clone https://github.com/miroqru/mauno
```

2. Устанавливаем зависимости (виртуальное окружение само подготовится):

```sh
uv sync
```

3. Копируем файл с настройками `.env.dist` в `.env`.
4. Вставляем в файл токен от бота и путь к набору стикеров.
4. Запускаем бота:

```sh
uv run -m maubot
```

5. Пишем небольшой скрипт для запуске демона через *systemd*.

> Вот и всё :)

Ах да, ещё вам потребуется включить `inline mode` для вашего бота и
обязательно выставить `inline feedback` на 100%.
Сделать это в [BotFather](https://t.me/BotFather).
Без этого, отправленные вами карты не будут обрабатываться ботом.

## Стикеры

> Больше не актуально, поскольку бот перешёл на генератор карт.

Кстати говоря, карточки для игры также были перерисованы.
Вы можете использовать их согласно следующей лицензии.

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="http://codeberg.org/salormoon/maubot">Maubot uno cards</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://t.me/mili_qlaster">Milinuri Nirvalen</a> is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block;">CC BY-NC-SA 4.0<img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""><img style="height:22px!important;margin-left:3px;vertical-align:text-bottom;" src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" alt=""></a></p>

Если вы захотите добавить свою колоду:
- Нарисуйте карточки и поместите их в папку `images/`, как c `progressive`.
- Укажите данные для авторизации в `api_auth.json`.
- Запустите скрипт для загрузки стикеров. Нужно будет загрузить 3 стикер пака для
  каждой директории.
- Собрать из полученных id файлов единый для колоды.
- Путь к собранному json файлу с id стикерами укажите в `.env` файле бота.
