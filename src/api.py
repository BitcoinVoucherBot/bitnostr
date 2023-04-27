#!/usr/bin/env python3

import requests
import json
import math
from .models import Order
from .settings import Settings
from .utils import Utils

class API:

    settings = Settings()

    def get_headers(self):
        
        self.settings.reload()

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.settings.bvb_api_key
        }
        return headers

    def create_lightning_order(self, amount, email, iban, user_public_key, lnaddress=None) -> Order:

        recipient_type = 1 if lnaddress is None else 2 
        recipient = user_public_key if lnaddress is None else lnaddress

        pub_key = Utils.npub_from_hex(user_public_key)

        url = "https://api.gwoq.com/v1/order/create_lightning"
        payload = {
            "event": "order.create",
            "payload": {
                'op_type': 'LA-D',
                'currency' : 'EUR',
                'email' : email,
                'iban' : iban,
                'amount' : str(amount),
                'public_key' : pub_key,
                'recipient': recipient,
                'recipient_type': recipient_type
            }
        }

        print('payload: ', payload)
        response = requests.post(url, json=payload, headers=self.get_headers())
        if response.status_code == 200:
            print('response ', response.text)
            result = json.loads(response.text)
            print('result - ', result)
            return result
        
        return None
    
    def cancel_order(self, order_id):
        url = "https://api.gwoq.com/v1/order/cancel"
        payload = {
            "event": "order.cancel",
            "payload": {
                "orderid" : order_id
            }
        }
        print('payload: ', payload)
        response = requests.post(url, json=payload, headers=self.get_headers())
        if response.status_code == 200:
            print('response ', response.text)
            result = json.loads(response.text)
            print('result - ', result)
            return result
        
        return None

    def notify_payment(self, order_id):
        url = "https://api.gwoq.com/v1/order/notify_payment"
        payload = {
            "event": "order.notify_payment",
            "payload": {
                "orderid" : order_id
            }
        }
        print('payload: ', payload)
        response = requests.post(url, json=payload, headers=self.get_headers())
        if response.status_code == 200:
            print('response ', response.text)
            result = json.loads(response.text)
            print('result - ', result)
            return result
        
        return None
    
    def get_fee(self):
        url = "https://api.gwoq.com/v1/order/getfee"
        response = requests.get(url, headers=self.get_headers())
        data = response.json()
        fee = data['fee']
        return fee
    
    def get_price(self):
        url = "https://api.gwoq.com/v1/order/getprice"
        response = requests.get(url, headers=self.get_headers())
        data = response.json()
        price = data['price']
        return price
    
    def get_mempool(self):
        url = "https://blockstream.info/api/mempool"
        response = requests.get(url)
        data = response.json()
        unitfee = math.ceil(data['total_fee']/data['vsize'])
        ret = f"📊 MEMPOOL STATUS\n\nCount: {data['count']} txs\nvsize (b): {self.convert_bytes(data['vsize'])}\nTotal Fees (sat): {data['total_fee']}\nAverage fees(sat/b): {unitfee}"
        return ret
    
    def get_miners_fees(self):
        url = "https://api.blockchain.info/mempool/fees"
        response = requests.get(url)
        data = response.json()
        ret = f"⛏ MINER FEES\n\nMinimum: {data['limits']['min']} sat/b\nMaximum: {data['limits']['max']} sat/b\nAverage: {data['regular']} sat/b\nAverage priority: {data['priority']} sat/b"
        return ret
    
    def get_stats(self):
        mempool = self.get_mempool()
        miners = self.get_miners_fees()
        return f"{miners}\n\n{mempool}"

    def convert_bytes(self, num):
        for x in ['bytes','KB','MB','GB','TB']:
            if num < 1024.0:
                return "%3.1f %s" % (num, x)
            num /= 1024.0

    def create_challenge(self):
        url = "https://api.gwoq.com/v1/order/challenge"
        response = requests.get(url, headers=self.get_headers())
        if response.status_code == 200:
            print('response ', response.text)
            result = json.loads(response.text)
            print('result - ', result)
            return result
        return None
    
    def create_on_chain_order(self, btc_address, email, iban, sig, message, public_key):
        pub_key = Utils.npub_from_hex(public_key)
        url = "https://api.gwoq.com/v1/order/create"
        payload = {
            "event": "order.create",
            "payload": {
                "bitcoin_address": btc_address,
                'currency': 'EUR',
                "email": email,
                "iban": iban,
                "message": message,
                "signature": sig,
                'public_key' : pub_key
            }
        }
        print('payload: ', payload)
        response = requests.post(url, json=payload, headers=self.get_headers())
        if response.status_code == 200:
            print('response ', response.text)
            result = json.loads(response.text)
            print('result - ', result)
            return result
        
        return None

