# SimpleQIWI: QIWI API for Humans
This is a simplest python module to receive and send QIWI payments
## Install
```
pip install SimpleQIWI
```
## Usage
### Getting balance
```python
from SimpleQIWI import *

token = "YOUR TOKEN HERE" # https://qiwi.com/api
phone = "YOUR PHONE"

api = QApi(token=token, phone=phone)

print(api.balance)

# Use api.full_balance to get more information about your wallets
```
### Sending payments
```python
from SimpleQIWI import *

token = "YOUR TOKEN HERE" # https://qiwi.com/api
phone = "YOUR PHONE"

api = QApi(token=token, phone=phone)

print(api.balance)

api.pay(account="Phone of recipient", amount=1, comment='This is a test!')

print(api.balance)
```
### Getting income payments
```python
from SimpleQIWI import *

token = "YOUR TOKEN HERE" # https://qiwi.com/api
phone = "YOUR PHONE"

api = QApi(token=token, phone=phone)

print(api.payments)
```
### Receiving payments
```python
from SimpleQIWI import *
from time import sleep

token = "YOUR TOKEN HERE" # https://qiwi.com/api
phone = "YOUR PHONE"

api = QApi(token=token, phone=phone)

price = 1
comment = api.bill(price)

print("Pay %i rub for %s with comment '%s'" % (price, phone, comment))

api.start() 

while True:
    if api.check(comment):
        print("Payment Received!")
        break
    
    sleep(1)

api.stop()
```
### Echo function
```python
from SimpleQIWI import *
from time import sleep

token = "YOUR TOKEN HERE" # https://qiwi.com/api
phone = "YOUR PHONE"

api = QApi(token=token, phone=phone)

price = 1
comment = api.bill(price)

print("Pay %i rub for %s with comment '%s'" % (price, phone, comment))


@api.bind_echo()
def foo(bar):
    print("New payment!")
    print(bar)
    api.stop()

api.start()
```
