#!/usr/bin/env python3
import requests
import os
import bech32, base64
from schwifty import IBAN
from nostr.nostr.key import PublicKey
from bitcoin.wallet import CBitcoinAddress, CBitcoinAddressError
from .signature import verify_message

class Utils:

    def validate_iban(self, iban):
        try:
            iban_to_check = IBAN(iban)
            ret = iban_to_check.validate()
            return ret
        except:
            return False

    def validate_email(self, email):
        if "@" not in email:
            return False
        if "." not in email:
            return False
        return True
    
    @classmethod
    def get_online_relays(self):
        url = 'https://api.nostr.watch/v1/online'
        response = requests.get(url)
        relays = list(response.json())
        return relays

    @classmethod
    def is_running_in_docker(self):
        env = os.environ.get('ENV', 'local')
        return False if env == 'local' else True


    @classmethod
    def npub_from_hex(self, hex):
        raw_bytes = bytes.fromhex(hex)
        converted_bits = bech32.convertbits(raw_bytes, 8, 5)
        pub_key = bech32.bech32_encode("npub", converted_bits)
        return pub_key
    
    @classmethod
    def hex_from_npub(self, npub):
        try:
            pk = PublicKey.from_npub(npub).hex()
            return pk
        except:
            return None
    
    @classmethod
    def remove_emoji(self, text):
        import unicodedata
        return ''.join(c for c in text if unicodedata.category(c) != 'So')
    
    @classmethod
    def validate_btc_address(self, address):
        try:
            CBitcoinAddress(address)
            return True
        except CBitcoinAddressError:
            return False
    
    @classmethod
    def verify_signature(self, address, signature_base64, message):
        ret = verify_message(address, signature_base64, message)
        return ret
