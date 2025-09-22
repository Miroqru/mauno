# Локальная установка

Итак, вы наигрались в Мау бота и полагаю решили попробовать запустить своего.
Благодаря открытому исходному коду у вас разумеется есть такая возможность.

!!! tip "Проявите уважение"

    - Если будете модифицировать бота, то пожалуйста сделайте **форк**.
    - А если просто будете использоваться, то укажите **автора**.
    - Взамен, мы будем оказывать вам поддержку.

Данная страница поможет вам установить и настроить свой проект.
Давайте же приступим к установке Telegram бота!

!!! note "А Docker?"

    Понимаю что у вас может быть страсть всё запускать через контейнеры.
    К сожалению мы пока не поддерживаем такой функционал.
    Но быть может в будущих версиях...

## Telegram бот

Здесь мы более детально рассмотрим процесс установки основного игрового бота.
Для работы с зависимостями и виртуальным окружением используется
[uv](https://docs.astral.sh/uv/).

1. Клонируем репозиторий на своё устройство:

```sh
git clone https://git,miroq.ru/mau/tg
```

2. Устанавливаем зависимости проекта (виртуальное окружение само подготовится):

```sh
uv sync
```

3. Копируем файл с настройками `.env.dist` в `.env`.
4. Укажите токен от вашего telegram бота.

```dotenv title=".env"
TELEGRAM_TOKEN = "YOUR TOKEN"
```

5. Теперь запускаем бота следующей командой:

```sh
uv run -m maubot
```

!!! warning "Inline mode"

    Ах да, ещё вам потребуется включить `inline mode` для вашего бота и
    обязательно выставить `inline feedback` на 100%.
    Сделать это в [BotFather](https://t.me/BotFather).
    Без этого, отправленные вами карты не будут обрабатываться ботом.

5. Пишем небольшой скрипт для запуске демона через _systemd_.

> Вот и всё :)

!!! note "Полагаю вы разбираетесь"

    Следующие действия опциональны и рассчитаны на тех, кто имеет
    имеет представление в представленных темах.
    Хотя это не отменя того, что при должном желании можно легко во всём
    разобраться.

### Webhook

Если вы хотите повысить скорость ответов бота, то ыв можете использовать
webhook.
Хорошо если у вас есть выделенный сервер с доменом в SSL сертификатом.
Или вы можете воспользоваться сервисами на подобии _Ngrok_ для предоставления
сервисов API туннелирования.

!!! tip "Webhook и Longpoll"

    Это два способа получения событий для бота.

    - **Longpoll**: Бот будет отправлять запросы на получение новых событий
      и ожидать, пока они не появятся.
    - **Webhook**: Telegram сам будет отправлять все события для бота
      на указанный адрес как только они появляются.

    Разумеется при таком раскладе webhook предпочтительнее.

ЧТобы настроить получение событий по webhook измените флаг `use_hook`.

```env title=".env"
use_hook = true
```

Дальше заполните следующие настройки.

| Параметр    | По умолчанию         | Описание                           |
| ----------- | -------------------- | ---------------------------------- |
| server_host | 127.0.0.1            | Какой хост будет случать хук.      |
| server_port | 3114                 | На каком порте будет работать хук. |
| hook_url    | https://mau.miroq.ru | Публичный URL хука.                |
| hook_root   | /webhook             | Путь хука, прибавляется к URL.     |
| hook_secret | super_secret         | Секретная фраза. для хука.         |

Пример настройки маршрута для **nginx**:

```conf
location /webhook {
    proxy_pass https://localhost:3114;
}
```

## Движок Mau

Если у вас появилось желание вместо бота поработать над библиотекой. то процесс
её установки схож с Telegram ботом.
Не будем слишком повторяться.

Кратко о том, как всё установить:

```sh
git clone https://git,miroq.ru/mau/mauno
cd mauno
uv sync
```

Рекомендуем заглянуть в раздел [API](../mau/index.md) для ознакомления с
функционалом движка.

!!! tip "А как тестировать?"

    Для тестов вы можете использовать Telegram бота.
    Для этого в uv добавьте ваш локальный движок как зависимость.
    Главное следите за кешированием.

## Mau-cards

Если вы хотите поднять свой сервер для карт, то загляните в
[репозиторий](https://git.miroq.ru/mau/cards) проекта.
О том как работать с сервером карт описано [здесь](card_generator.md).

## Стикеры

!!! info "Устаревший раздел"

    Больше не актуально, поскольку бот перешёл на генератор карт.
    Можете просто ознакомиться с материалом.

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
