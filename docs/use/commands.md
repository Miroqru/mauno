# Команды бота

Для использования бота есть следующие команды.

В данном контексте *комната* и *игры* являются синонимами.
Однако лучше не смешивать данные понятия.

> `*` - Команда доступна только владельцам комнаты.

## `/game`

Создаёт новую комнату в чате.
Будет отправлено сообщение лобби.
Если комната уже существует, отправит новое сообщение лобби.

## `/join`

Зайти в комнату.
Также можно воспользоваться кнопкой в сообщении лобби.
Зайти можно как до начала игры, так и во время игры, если комната открыта.

## `/start_game`

Начинает новую игру в комнате.
Также можно воспользоваться кнопкой в сообщении лобби.
Обратите внимание что начать игру может каждый активный игрок.

## `/leave`

игрок покидает комнату.
Это действие засчитывается как проигрыш игрока.

## `/skip` `*`

Пропускает текущего игрока.
Помимо пропуска игрок также берёт необходимое количество карт +1.
Если игра приостановилась на выборе цвета - будет выбран случайный цвет.
Ход передаётся следующему игроку.

Бывает полезно, когда игрок долго не ходит.

## `/kick` `*`

Перешлите сообщение игрока, которого хотите исключить из игры.
Для игрока это будет считаться аналогично проигрышу.
Ход будет передан следующему игроку.

## `/close` `*`

Закрывает комнату для новых игроков.
До окончания игры игроки не смогут присоединиться к комнате.
Бывает полезно, чтобы уже выигравшие/проигравшие игроки не заходили повторно.

## `/open` `*`

Открывает комнату для всех игроков.
теперь новые игроки смогут заходить в комнату.
А ещё это значит что ранее выигравшие/проигравшие тоже смогут зайти.
Повторный заход в игру никак не контролируется.

## `/rules` `*`

Отправляет сообщение с выбранными игровыми правилами.
Аналогично кнопке выбора правил в сообщении лобби.
Будьте осторожны, поскольку правила можно изменять прямо в процессе
игры.

## `/stop` `*`

Принудительно завершает игру.
Фактически вызывается метод `game.end()`.
Все оставшиеся игроки становятся проигравшими.
В чат отправляется сообщение с результатами игры.

Бывает полезно если игра затягивается или надо остановить хаос.

## `/help`

В личные сообщения пользователя отправит небольшую справку по игре.
В ней содержатся простые шаги как пользователь может начать играть.
Также из справки можно узнать о самых часто используемых командах.

## `/status`

В чат будет отправлено сообщение с основной информацией о боте.
Включает в себя версию, цель проекта, ссылки на исходный код.
