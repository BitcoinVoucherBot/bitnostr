#!/usr/bin/env python3

from typing import List
from enum import IntEnum

class OrderType(IntEnum):
    UNKNOWN = 0
    LIGHTNING = 1
    ON_CHAIN = 2

class Command():
    command = ""
    amount = 0
    iban: str = None
    lud16: str = None
    lud06: str = None
    email: str = None
    order_type: OrderType = OrderType.UNKNOWN
    message: str = None
    signature: str = None

class Order(object):
    call = ""
    order_time = ""
    orderid = ""
    payment_description = ""
    payment_method = None
    status = ""

    def __init__(self, call, order_time, orderid, payment_description, payment_method, status):
        self.call = call
        self.order_time = order_time
        self.orderid = orderid
        self.payment_description = payment_description
        if payment_method is not None or payment_method != "":
            self.payment_method = PaymentMethod(**payment_method)
        self.status = status

class PaymentMethod(object):
    creditor_address = ""
    creditor_bank_bic = ""
    creditor_bank_country = ""
    creditor_bank_iban = ""
    creditor_bank_name = ""
    creditor_name = ""

    def __init__(self, creditor_address, creditor_bank_bic, creditor_bank_country, creditor_bank_iban, creditor_bank_name, creditor_name):
        self.creditor_address = creditor_address
        self.creditor_bank_bic = creditor_bank_bic
        self.creditor_bank_country = creditor_bank_country
        self.creditor_bank_iban = creditor_bank_iban
        self.creditor_bank_name = creditor_bank_name
        self.creditor_name = creditor_name

class OrderComplete(object):
    orderid = ""
    public_key = ""
    fiat = 0
    sale_bitcoin = 0
    price = 0
    recipient = ""
    recipient_type = 1 #1=nostr pub, #2=lnaddress, 0=onchain-address
    payment_hash= ""

    def __init__(self, orderid, public_key, fiat, sale_bitcoin, price, recipient, recipient_type, payment_hash):
        self.orderid = orderid
        self.public_key = public_key
        self.fiat = fiat
        self.sale_bitcoin = sale_bitcoin
        self.price = price
        self.recipient = recipient
        self.recipient_type = recipient_type
        self.payment_hash = payment_hash
