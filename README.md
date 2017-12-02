# SimpleQIWI: QIWI API for Humans
Эта библеотека позволит вам производить транзакции и принимать платежи без регистрации магазина.
## Установка
```bash
pip install SimpleQIWI
```
## Использование
### Получение баланса
```python
from SimpleQIWI import *

token = "ВАШ ТОКЕН"         # https://qiwi.com/api
phone = "ВАШ ТЕЛЕФОН"

api = QApi(token=token, phone=phone)

print(api.balance)

# Используйте api.full_balance чтобы получить больше информации о кошельках. 
```
### Переводим деньги на счета QIWI
```python
from SimpleQIWI import *

token = "ВАШ ТОКЕН"         # https://qiwi.com/api
phone = "ВАШ ТЕЛЕФОН"

api = QApi(token=token, phone=phone)

print(api.balance)

api.pay(account="ТЕЛЕФОН ПОЛУЧАТЕЛЯ", amount=1, comment='Привет мир!')

print(api.balance)
```
### Получаем входящие платежи
```python
from SimpleQIWI import *

token = "ВАШ ТОКЕН"         # https://qiwi.com/api
phone = "ВАШ ТЕЛЕФОН"

api = QApi(token=token, phone=phone)

print(api.payments)
```
### Принемаем платежи
```python
from SimpleQIWI import *
from time import sleep

token = "ВАШ ТОКЕН"         # https://qiwi.com/api
phone = "ВАШ ТЕЛЕФОН"

api = QApi(token=token, phone=phone)

price = 1                   # Минимальное значение при котором счет будет считаться закрытым
comment = api.bill(price)   # Создаем счет. Комментарий с которым должен быть платеж генерируется автоматически, но его можно задать                                 # параметром comment. Валютой по умолчанию считаются рубли, но ее можно изменить параметром currency

print("Переведите %i рублей на счет %s с комментарием '%s'" % (price, phone, comment))

api.start()                 # Начинаем прием платежей

while True:
    if api.check(comment):  # Проверяем статус
        print("Платёж получен!")
        break
    
    sleep(1)

api.stop()                  # Останавливаем прием платежей
```
### Эхо
```python
from SimpleQIWI import *
from time import sleep

token = "ВАШ ТОКЕН"         # https://qiwi.com/api
phone = "ВАШ ТЕЛЕФОН"

api = QApi(token=token, phone=phone)

price = 1
comment = api.bill(price)

print("Pay %i rub for %s with comment '%s'" % (price, phone, comment))


@api.bind_echo()            # Создаем эхо-функцию.  Она будет вызываться при каждом новом полученном платеже. В качестве аргументов ей
                            # передаётся информация о платеже. 
def foo(bar):
    print("New payment!")
    print(bar)             
    api.stop()

api.start()
```
