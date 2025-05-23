# Генератор карт

![cream put 4](https://mau.miroq.ru/card/next/7_4_4_put/cover)

> https://mau.miroq.ru/card/next/7_4_4_put/cover

Вы могли заметить что карты состоят из общих компонентов.

- Основание карты.
- Подложка цвета.
- Символы верхнего угла.
- Символы нижнего угла.
- Глиф.

Генератор карт занимается сборкой карт из уже готовых асетов.
Это позволяет добиться большей гибкости.

Генератор напрямую не связан с движком, пересекаются они только в формате
сохранения карт в виде строки.

> Репозиторий [mau-cards](https://git.miroq.ru/rumia/mau-cards).


## Использование

На самом деле использовать генератор достаточно просто.
Ссылка на изображение представлена в следующем формате:

`https://mau.miroq.ru/card/{asset}/{card}/{filter}`

**Где**:

- `{asset}`: Это набор асетов, сейчас доступны `progressive`, `next`.
- `{card}`: Описание карты, о нем поговорим дальше.
- `{filter}`: Эффект для карты. Доступны `cover`, `uncover`.

**Формат карта**: `{color}_{value}_{cost}_{type}`.

- Цвет от 0 до 7.
- Значение карты от 0 до 9.
- Стоимость карты от 0 до 99.
- Тип карты.

Доступные типы карт:

- `number`: Числовая карта.
- `twist`: Обмен картами с другим игроком.
- `rotate`: Обмен картами оо всеми игроками.
- `block`: Пропуск хода.
- `color`: Карта простой смены цвета.
- `delta`: Особая карта (пока нет применения).
- `reverse`: Разворот порядка ходов.
- `take`: Взять карты.
- `put`: Положить карты.
- `wild+color`: дикий выбор цвета.
- `wild+take`: Дикое взятие карт.

## Мотивация

Долгое время использовались нарисованные карты-стикеры.
Они выглядели очень канонично и для стороннего наблюдателя всё выглядело словно участники только и отправляют стикеры в чат.
Однако здесь же кроется и **главная проблема**. Использовать во время игры можно только те карты, что есть в стикер паке.

Генерация карт же с другой стороны предлагают большую гибкость.
Вместе с тем часто используемые карты кешируются для повторного использования.

## Асеты

Теперь рассмотрим как генератор хранит асеты карт для сборки.

В корне проекта есть директория `assets/`.
Каждая директория внутри представляет собой отдельный набор асетов для карт.
Если директория называется `progressive`, то в ссылке стоит указывать:
`mau.miroq.ru/card/progressive/...`

### `base.png`

- Размер: 312 x 512

Подложка для карты.
Используется как основа для всех карт.

### `color/`

- Размер: 312 x 512

Цветовая подложка для карты.
Название файла совпадает с порядковым номером цвета.

Для `mau v2.3` это:

0. красный.
1. Оранжевый.
2. Жёлтый.
3. Зелёный.
4. Голубой.
5. Синий.
6. Чёрный.
7. Кремовый.

при том 6 (чёрный) используется как основный цвет для диких карт.

### `sym/`

- Размер не больше 64 x 64.
- Не Зависят от цвета карты.

используются как символы верхнего левого углы.
Название файла соответствует назначению.
Во время сборки могут комбинироваться до 3з символов на карте.

- `0` .. `9`: Числовые символы.
- `block`: Символ карты пропуска хода.
- `color`: Карта смены цвета. Простая и дикая.
- `delta`: Для особого типа карт.
- `minus`: Для карт типа `put`. Противоположность взятию.
- `plus`: Для карт типа `take`. В том числе и `wild+take`.
- `reverse`: Для карт разворота. Также помечаются карты обмена между игроками.

### `sym_reverse/`

- Размер не больше 64 x 64.
- Не зависят от цвет карты.

используются как символы правого нижнего угла.
Аналогичны `sym/`, однако символы должны быть перевёрнуты.
Во время сборки могут комбинироваться до 3з символов на карте.

### `glyph/`

- Размер не больше 160 x 160.

Главный символ карты.
В отличие от небольших символов, уникальный для каждого типа карты. (почти)

Для диках карт:

- `color`: Дикая карта выбора цвета.
- `take_1/2/4`: Для карт `wild+take` в варианте взять 1, 2+, 4+.

С привязкой к цвету:

- `0` .. `9`: Для числовых карт.
- `block`: Для карт пропуска хода.
- `color`: Для карты выбора текущего цвета. (упрощённый вариант дикой)
- `delta`: Особый вид карты.
- `reverse`: Карта разворота порядка ходов.
- `take_1/2/4`: Варианты карты взять/положить для 1, 2+, 4+.

## Генератор карт

Проект написан на Go с использованием фреймворка Fiber.
Для кеширования карт используется Redis база данных.

> Может появится больше подробностей.
