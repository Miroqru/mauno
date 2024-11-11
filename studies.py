# комментарии ----------------------------------------------------------
# Просто для пояснения.
# не влияют на код и нужны программистам.


# [0] Привет мир -------------------------------------------------------
print("Hello world!")


# [1] Вывод на печать --------------------------------------------------
print(12, True)
print("Кусь", "мусь", 12)


# [2] Базовые типы данных ----------------------------------------------

# Целые числа - int
print(12, -12)

# Числа с плавающей точкой - float
print(12.35, -119.73)

# Строки - str
print("Приветик")

# Логический (булевый) тип - bool
print(True, False)

# Пустота - None
print(None)


# [3] Арифметические операции ------------------------------------------

print(2 + 2)
print(2 - 3)
print(4 * 5)
print(2 ** 3) # возведение в степень
print(21 / 2) # Результат будет с плавающей точкой
print(23 // 2) # Мы тут получим целое число
print(round(23 // 2)) # Мы тут получим целое число
print(29 % 3) # Остаток

# бонус
d, m = divmod(23, 9)


# [4] Переменные -------------------------------------------------------

num: int = 12 * 3 + 5 / 2 # int
num_formula: str = "12 * 3 + 5 / 2" # str
some_long_variable_name: float = 9.11 # float
ENABLE_EXPERIMENTAL_OPTIONS: bool = True # bool (constant)

print("Формула:", num_formula, "результат:", num)

# [5] Строки -----------------------------------------------------------

print("Формула:", num_formula, "результат:", num)
some_str = "Формула: " + num_formula + "результат: " + str(num)
some_str: str = f"Формула: {num_formula} результат: {num}" # 2 -> "2"

print(some_str)

# Длинные строки
some_long_str = (
    "Created a new game!\n"
    "Join the game with /join and start the game with /start"
)

# [6] Ввод и вывод -----------------------------------------------------

a = int(input("Первое число: ")) # 2
b = int(input("Второе число: ")) # 3
print(f"результат: {a + b}") # 5


# [7] ветвление --------------------------------------------------------

# == != > < >= <= is : операторы сравнения
# and or not         : логические операторы

bal = 50

hamburger_cost = 247
chocolate_cost = 73
bread_cost     = 24
bubblegum_cost = 5

if bal >= hamburger_cost:
    bal -= hamburger_cost
    print("Сегодня я очень вкусно покушаю гамбургер")

elif bal >= chocolate_cost:
    bal -= hamburger_cost
    print("Ничего, шоколадка даже вкуснее <3")

elif bal >= bread_cost:
    bal -= bread_cost
    print("Ну не страшно, сегодня похаваю пол батона")

elif bal >= bubblegum_cost:
    bal -= bubblegum_cost
    print("Зато буду вкусно пахнуть")

else:
    print("Сегодня не кушаю :(")

print("На балансе осталось:", bal)

# [8] чиклы ------------------------------------------------------------

a = 1000
while a > 0:
    print(f"{a} - 7 = {a-7}")
    a -= 7

for a in range(1000, 0, -7):
    print(f"{a} - 7 = {a-7}")

fruits = ["banana", "apple", "qiwi", "pineapple"]
for i, fruit in enumerate(fruits):
    print(i, fruit)


# [9] Контейнеры -------------------------------------------------------

some_list = ["apple", "banana"]
some_dict = {"+1": "Anna"}
some_tuple = ("easy", "normal", "hard")
some_set = {"apple", "banana"}


# [10] список ----------------------------------------------------------

some_list = [
    "apple", "banana", "ananas", "pineapple"
]

print(some_list)
print(some_list[0]) # apple
print(some_list[0:3]) # apple, banana

# slices
# start:stop:step
# 0:3 (:1)
# 2:
# :3
# ::

list_2 = some_list.copy()
some_list[2] = "orange"

some_list.append("watermelon")
some_list.insert(2, "amogus")
fruit = some_list.pop()


# [11] словарь ---------------------------------------------------------

contacts = {
    "+3233412": "John",
    "+3434212": "Marie",
    0: "Anna"
}

name = contacts["+3233412"] # John
name = contacts[0] # Anna

name = contacts.get("2", "Smith")
name = contacts.get("3") # None

# итераторы словаря
keys = contacts.keys()
keys = contacts.values()
keys = contacts.items()

for name in contacts.values():
    print(name) # John Marie Anna

for number, name in contacts.items():
    print(number, name)
    if name == "Anna":
        print(number)

contacts["2"] = "Smith"
contacts.pop(0) # Anna


# [12] кортеж ----------------------------------------------------------

states = ("easy", "normal", "hard")
states[1] # normal

distance = (12, "m")

class Dist(NamedTuple):
    value: int
    mod: str

distance = Dist(12, "m")


# [13] множество -------------------------------------------------------

states = {"easy", "normal", "hard"}
states[0]
states.add("extreme")
states.pop()


# [14] функции ---------------------------------------------------------

some_fruits = [
    "apple", "banana", "ananas", "apple", "pineapple", "orange", "banana"
]

def clear_list(l: list) -> list:
    res = []

    for element in items:
        if element in res:
            continue

        res.append(element)

    return res

cleared_list = clear_list(name="John", some_arg=1)


# [15] итераторы -------------------------------------------------------

numbers = [2, 5 ,7, 1, 4, 3, 11, 8, 6, 9, 5, 10]

def more_then(numlist: Iterable[int], min_num: int) -> int:
    for num in numlist:
        if num > min_num:
            yield num

new_nums = list(more_then(numbers, 5))


# [16] декораторы ------------------------------------------------------

def log(f):
    def wrapper():
        print("Func started")
        f()
        print("Func finished")
    return wrapper

logged_more_than = log(more_then)

# [17] классы ----------------------------------------------------------


# [18] импорты ---------------------------------------------------------
