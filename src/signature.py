#!/usr/bin/env python3

import base64
from electrum.electrum import ecc, util

from bitcoin.wallet import CBitcoinSecret, P2PKHBitcoinAddress
from bitcoin.signmessage import BitcoinMessage, VerifyMessage, SignMessage
#https://github.com/petertodd/python-bitcoinlib/blob/master/examples/sign-message.py

def verify_message(address, signature, message):
    # signature verification through electrum
    sig = base64.b64decode(signature)
    message = util.to_bytes(message)
    return ecc.verify_message_with_address(address, sig, message)


def sign_message(key, msg):
    # sign message with bitcoinlib. key is WIF key
    secret = CBitcoinSecret(key)
    message = BitcoinMessage(msg)
    return SignMessage(secret, message)


def print_verbose(signature, key, msg):
    secret = CBitcoinSecret(key)
    address = P2PKHBitcoinAddress.from_pubkey(secret.pub)
    message = BitcoinMessage(msg)
    print('Verified: %s' % VerifyMessage(address, message, signature))


def verify_message_signature(address, signature, message):
    # works if legacy address is provided, otherwise doesnt
    msg = BitcoinMessage(message)
    return VerifyMessage(address, msg, signature)    # sign message with bitcoinlib. key is WIF key
    secret = CBitcoinSecret(key)
    message = BitcoinMessage(msg)
    return SignMessage(secret, message)


def print_verbose(signature, key, msg):
    secret = CBitcoinSecret(key)
    address = P2PKHBitcoinAddress.from_pubkey(secret.pub)
    message = BitcoinMessage(msg)
    print('Verified: %s' % VerifyMessage(address, message, signature))


def verify_message_signature(address, signature, message):
    # works if legacy address is provided, otherwise doesnt
    msg = BitcoinMessage(message)
    return VerifyMessage(address, msg, signature)