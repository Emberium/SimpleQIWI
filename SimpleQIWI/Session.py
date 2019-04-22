#!/usr/bin/env python
# -*- coding: utf-8 -*-

from uuid import uuid4
from SimpleQIWI import OverridingEx, InvalidTokenError, ArgumentError, QIWIAPIError
import requests
import threading
import time


class QApi(object):

    def __init__(self, token, phone, delay=1):
        """
        Class init

        :type token: str
        :type phone: str
        :type delay: int

        :param token: QIWI API token
        :param phone: Your phone [required for pay() function]
        :param delay: Loop sleep time
        """

        self._s = requests.Session()

        self._s.headers['Accept'] = 'application/json'
        self._s.headers['Content-Type'] = 'application/json'
        self._s.headers['Authorization'] = 'Bearer ' + token

        self.phone = phone

        self._inv = {}

        self._echo = None

        self.delay = delay

        self.thread = False

    @property
    def _transaction_id(self):
        """
        Generates transaction id for pay() function.

        :return: UNIX time * 1000
        """

        return str(int(time.time() * 1000))

    @property
    def payments(self):
        """
        Returns income payments

        :return: income payments (dict)
        """

        return self._get_payments()

    @property
    def full_balance(self):
        """
        Returns full account balance info

        :return: balance (dict)
        """

        return self._get_balance()

    @property
    def balance(self):
        """
        Returns balances from all accounts

        :return: balances (list)
        """

        balances = self.full_balance
        balance = []

        for wallet in balances:
            if wallet['balance'] is not None:
                balance.append(wallet['balance']['amount'])

        return balance

    def bill(self, price, comment=uuid4(), currency=643):
        """
        Generates bill

        :type price: int
        :type comment: str
        :type currency: int

        :param price: Minimum price of your service.
        :param comment: Comment for payment
        :param currency: Currency
        :return: Comment
        """

        comment = str(comment)

        if comment in self._inv:
            raise OverridingEx('Overriding bill!')

        self._inv[comment] = {
            'price': price,
            'currency': currency,
            'success': False
        }

        return comment

    def _get_balance(self):
        """
        Returns full account balance info

        :return: balance (dict)
        """

        response = self._s.get('https://edge.qiwi.com/funding-sources/v1/accounts/current')

        if response is None:
            raise InvalidTokenError('Invalid token!')

        json = response.json()

        if 'code' in json or 'errorCode' in json:
            raise QIWIAPIError(json)

        balances = []

        for account in json['accounts']:
            if account['hasBalance']:
                balances.append({
                   'type': account['type'],
                   'balance': account['balance']
                })

        return balances

    def _get_payments(self, rows=20):
        """
        Returns income payments

        :type: rows: int: 1-50

        :param: rows: Count of payments in response
        :return: income payments (dict)
        """

        post_args = {
            'rows': rows,
            'operation': 'IN'
        }

        response = self._s.get(
            url='https://edge.qiwi.com/payment-history/v1/persons/%s/payments' % self.phone,
            params=post_args
        )

        data = response.json()

        if 'code' in data or 'errorCode' in data:
            raise QIWIAPIError(data)

        return data

    def bind_echo(self):
        """
        Binds an echo function

        :return: decorator
        """

        def decorator(func):
            if func.__code__.co_argcount != 1:
                raise ArgumentError('Echo function must have one argument!')

            self._echo = func

        return decorator

    def pay(self, provider, account, amount, fields=None, currency='643', comment=None, tp='Account', acc_id='643'):
        """
        Transfer to QIWI Wallet

        :type provider: str
        :type account: str
        :type amount: int
        :type currency: str
        :type comment: str
        :type tp: str
        :type acc_id: str
        :type fields: dict
        
        :param provider: Provider ID (e.g. https://qiwi.com/payment/form/26580 = 26580) 
        :param account: Phone number of payee
        :param amount: Amount of money for transaction
        :param currency: Currency
        :param comment: Comment for transaction
        :param tp: Type of payee
        :param acc_id: Currency
        :param fields: whatever you need

        :return: response
        """

        post_args = {
            "id": self._transaction_id,
            "sum": {
                "amount": amount,
                "currency": currency
            },
            "paymentMethod": {
                "type": tp,
                "accountId": acc_id
            },
            "fields": {
                "account": account
            }
        }

        if comment is not None:
            post_args['comment'] = comment

        if fields is not None:
            for key,value in fields.items():
                post_args['fields'][key] = value

        if provider is not None:
            url = 'https://edge.qiwi.com/sinap/api/v2/terms/'+provider+'/payments'
        else:
            url= 'https://edge.qiwi.com/sinap/api/v2/terms/99/payments'

        response = self._s.post(
            url=url,
            json=post_args
        )

        data = response.json()

        if 'code' in data or 'errorCode' in data:
            raise QIWIAPIError(data)

        return response.json()

    def check(self, comment):
        """
        Check payment

        :param comment: Payment comment
        :return: bool
        """

        if comment not in self._inv:
            return False

        return self._inv[comment]['success']

    def _async_loop(self, target):
        lock = threading.Lock()

        while self.thread:
            try:
                lock.acquire()

                target()

            finally:
                lock.release()

    def _parse_payments(self):
        payments = self.payments

        if 'errorCode' in payments:
            time.sleep(10)
            return

        for payment in payments['data']:

            if payment['comment'] in self._inv:

                if payment['total']['amount'] >= self._inv[payment['comment']]['price'] and payment['total']['currency'] == \
                        self._inv[payment['comment']]['currency'] and not self._inv[payment['comment']]['success']:

                    self._inv[payment['comment']]['success'] = True

                    if self._echo is not None:
                        self._echo({
                            payment['comment']: self._inv[payment['comment']]
                        })

        time.sleep(self.delay)

    def start(self):
        """
        Starts thread
        """

        if not self.thread:
            self.thread = True
            th = threading.Thread(target=self._async_loop, args=(self._parse_payments,))
            th.start()

    def stop(self):
        """
        Stops thread
        """
        self.thread = False
