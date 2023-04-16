#!/usr/bin/env python3

import requests

class Bitcoin:
    
    def get_price(self):
        url = 'https://api.coindesk.com/v1/bpi/currentprice.json'
        response = requests.get(url)
        data = response.json()
        price = data['bpi']['EUR']['rate']
        return price