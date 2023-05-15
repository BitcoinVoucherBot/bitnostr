#!/usr/bin/env python3

import re
import time
import datetime
import json
import redis as r
from .btc import Bitcoin
from .core.bot import NostrCoreBot
from .models import Command, Order, OrderComplete, OrderType
from .api import API
from .utils import Utils
from .settings import Settings
from nostr.nostr.event import Event, EventKind
from nostr.nostr.key import PublicKey

class Bot(NostrCoreBot):

        settings = Settings()

        commands = {}
        amounts = {}
        disclaimer = "Please note that payment must come from your own bank account. Third parties payments not allowed. Condition gets accepted when going forward.\n\n❗️Sepa under credit cards (ex. postepay,etc) are not allowed and will be rejected"
        quick_links = "Quick Menu:\n\n/start 🚀 Start new procedure: /start\n/email ✉️ Set your email: /email <email>\n/iban 🏦 Set your iban: /iban <iban>\n/info ℹ️ Get current details: /info\n\n/stats 📊 Miner fees: /stats\n/price 💰 BTC/EUR price: /price\n\n/push ⚡️ Push Sats to your Lightning Address: /push\n/swap 🔗 Push Bitcoin to your on-chain address: /swap\n\n/help 📖 Read this help: /help\n/tos 📃 Terms Of Service: /tos\n/support 🛟 Support channels: /support"
        error_message = "I don't know that command. Try /help"
        support_message = "🛟 Support\n\nIn order to contact us for specific support questions please open a ticket on Telegram at:\nhttps://t.me/VoucherSupportBot\n\nAlso please join our Telegram discussion group\nhttps://t.me/BitcoinVoucherGroup\n\nYour public key is:\n[pub_key]"
        error_message_proceed = f"❌ ERROR.\n\nThere was an error with the order. Please try again.\n\n{quick_links}"

        api = API()
        utils = Utils()
        lightning_tiers = settings.lightning_tiers
        on_chain_tiers_first = settings.on_chain_tiers_first
        on_chain_tiers_others = settings.on_chain_tiers_others
        
        redis_host = 'redis' if utils.is_running_in_docker() else '127.0.0.1'
        redis = r.Redis(host=redis_host, port=6379, db=0)

        def __init__(self):
            super().__init__()

        def process_metadata(self, event, metadata):
            created_at = metadata['created_at']
            if 'lud16' in metadata:
                self.set_lud16(event, lud16=metadata['lud16'].replace('\"', '"'))
            if 'lud06' in metadata:
                self.set_lud06(event, lud06=metadata['lud06'].replace('\"', '"'))
            if 'display_name' in metadata:
                self.set_display_name(event, display_name=metadata['display_name'].replace('\"', '"'))
            if 'name' in metadata:
                self.set_name(event, name=metadata['name'].replace('\"', '"'))
            if 'nip05' in metadata:
                if 'nip05valid' not in metadata:
                    self.set_nip05(event, nip05=metadata['nip05'].replace('\"', '"'))
                elif metadata['nip05valid'] == 'true' or metadata['nip05valid'] == True:
                    self.set_nip05(event, nip05=metadata['nip05'].replace('\"', '"'))
            
            self.set_profile(event, json.dumps(metadata), created_at)
                    
    
        def process_message(self, event, decrypted_message):
            if event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                print(f"Preparing reply to {event.public_key} / {event.id}")
                is_command = decrypted_message.strip().lower().startswith("/")
                if is_command:
                    command = decrypted_message.strip().lower().removeprefix("/")
                    if self.settings.enabled is False:
                        if self.verify_admin(event):
                            if command.find("admin/enable") != -1:
                                val = command.split(" ")[1]
                                if val == "true":
                                    self.settings.set_enabled(True)
                                self.send_message(recipient_pubkey=event.public_key, cleartext_content=f"Enabled: {self.settings.enabled}")
                        else:
                            self.show_disabled_message(event)
                        return
                    
                    if command == "start" or command == "help" or command == "welcome":
                        self.get_profile(event.public_key)
                        time.sleep(0.1)
                        self.show_welcome_message(event)
                    elif command == "profile":
                        self.get_profile(event.public_key)
                    elif command == "cancel":
                        self.show_cancel_message(event)
                    elif command == "price":
                        self.show_btc_price(event) 
                    elif command == "purchase":
                        self.show_purchase_service(event, command=command)
                    elif command == "push":
                        self.show_purchase(event, command=command, type=OrderType.LIGHTNING)
                    elif command == "swap":
                        self.show_purchase(event, command=command, type=OrderType.ON_CHAIN)
                    elif command == "continue":
                        self.show_proceed(event)
                    elif command == "proceed":
                        self.show_provide_details(event) 
                    elif command == "verify":
                        self.get_challenge_token(event)
                    elif command.find("email") != -1:
                        if command == 'email':
                            self.show_provide_email(event, override_email=True)
                        else:
                            email = command.split(" ")[1]
                            self.show_email_confirmation(event, email, show_proceed=False)
                    elif command.find("iban") != -1:
                        if command == 'iban':
                            self.show_provide_iban(event, override_iban=True)
                        else:
                            iban = command.split(" ")[1].upper()
                            self.show_iban_confirmation(event, iban, show_proceed=False)
                    elif command == "info":
                        self.show_info(event)
                    elif command == "tos":
                        self.show_tos(event)
                    elif command == "notify":
                        self.notify_payment(event)
                    elif command == "retry":
                        self.get_profile(event.public_key)
                        self.send_message(recipient_pubkey=event.public_key, cleartext_content="Please wait...")
                        time.sleep(2.0)
                        self.show_proceed(event)
                    elif command == "stats":
                        self.show_stats(event)
                    elif command == "support":
                        self.show_support(event)
                    elif command.find("admin/enable") != -1:
                        val = command.split(" ")[1]
                        if self.verify_admin(event):
                            if val == "false":
                                self.settings.set_enabled(False)
                            self.send_message(recipient_pubkey=event.public_key, cleartext_content=f"Enabled: {self.settings.enabled}")
                    elif re.match(r'^[0-9]+$', command):
                        if self.is_amount_valid(event, command):
                            self.show_amount_confirmation(event, command, show_proceed=True)
                    else:
                        self.send_message(recipient_pubkey=event.public_key, cleartext_content=self.error_message)
                else:
                    try:
                        if len(self.commands) > 0 and event.public_key in self.commands.keys():
                            self.start_subprocess(event, decrypted_message, override=True)
                        else:
                            self.send_message(recipient_pubkey=event.public_key, cleartext_content=self.error_message)
                    except Exception as e:
                        print(e)
                        self.send_message(recipient_pubkey=event.public_key, cleartext_content=self.error_message)
                
            self.set_last_message_created_at(event=event)

        def set_command(self, event, command, order_type=OrderType.UNKNOWN, message=None, signature=None):
            if event.public_key not in self.commands or self.commands[event.public_key] is None:
                self.commands[event.public_key] = Command()

            cmd = self.commands[event.public_key]
            cmd.command = command
            if order_type != OrderType.UNKNOWN:
                cmd.order_type = order_type
            if message:
                cmd.message = message
            if signature:
                cmd.signature = signature
            self.commands[event.public_key] = cmd
        
        def set_amount(self, event, value):
            if event.public_key not in self.commands or self.commands[event.public_key] is None:
                self.commands[event.public_key] = Command()

            cmd = self.commands[event.public_key]
            cmd.command = "purchase"
            cmd.amount = value
            self.commands[event.public_key] = cmd

            self.amounts[event.public_key] = value
        
        def set_iban(self, event, value):
            if event.public_key not in self.commands or self.commands[event.public_key] is None:
                self.set_command(event, "set_iban")

            cmd = self.commands[event.public_key] or Command()
            cmd.command = "set_iban"
            cmd.iban = value
            self.commands[event.public_key] = cmd
            if value is not None:
                self.redis.hset(event.public_key, "iban", value)

        def set_email(self, event, value):
            if event.public_key not in self.commands or self.commands[event.public_key] is None:
                self.set_command(event, "set_email")

            cmd = self.commands[event.public_key] or Command()
            cmd.command = "set_email"
            cmd.email = value
            self.commands[event.public_key] = cmd

            if value is not None:
                self.redis.hset(event.public_key, "email", value)
        
        def set_lud16(self, event, lud16):
            if event.public_key not in self.commands or self.commands[event.public_key] is None:
                self.set_command(event, "set_address")

            cmd = self.commands[event.public_key] or Command()
            cmd.command = "set_address"
            if cmd.lud16 is not lud16:
                cmd.lud16 = lud16
            self.commands[event.public_key] = cmd

            if lud16 is not None:
                self.redis.hset(event.public_key, "lud16", lud16)
        
        def set_lud06(self, event, lud06):
            if event.public_key not in self.commands or self.commands[event.public_key] is None:
                self.set_command(event, "set_address")

            cmd = self.commands[event.public_key] or Command()
            cmd.command = "set_address"
            if cmd.lud06 is not lud06:
                cmd.lud06 = lud06
            self.commands[event.public_key] = cmd

        def set_display_name(self, event, display_name):
            self.redis.hset(event.public_key, "display_name", display_name)
        
        def set_name(self, event, name):
            self.redis.hset(event.public_key, "name", name)

        def set_nip05(self, event, nip05):
            self.redis.hset(event.public_key, "nip05", nip05)

        def set_profile(self, event, metadata, created_at):
            profile_created_at = self.redis.hget(event.public_key, "profile_created_at")
            profile_created_at = int(profile_created_at) if profile_created_at is not None else None
            if profile_created_at is not None and profile_created_at > created_at:
                return
            self.redis.hset(event.public_key, "profile", metadata)
            self.redis.hset(event.public_key, "profile_created_at", created_at)

        def set_btc_address(self, event, address):
            self.redis.hset(event.public_key, "btc_address", address)

        def reset_command(self, event):
            self.commands[event.public_key] = None

        def is_first_order(self, event):
            orders = self.redis.lrange(f"{event.public_key}:orders", 0, -1)
            ret = True if len(orders) == 0 else False
            return ret

        def is_amount_valid(self, event, amount):
            cmd = self.commands[event.public_key]
            lower = self.lightning_tiers[0]
            upper = self.lightning_tiers[1]
            if cmd.order_type == OrderType.ON_CHAIN:
                if self.is_first_order(event):
                    lower = self.on_chain_tiers_first[0]
                    upper = self.on_chain_tiers_first[1]
                else:
                    lower = self.on_chain_tiers_others[0]
                    upper = self.on_chain_tiers_others[1]
            try:
                val = int(amount)
                if val >= lower and val <= upper:
                    return True
                else:
                    message = f"Please enter a valid amount between {lower} and {upper}."
                    self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
                    return False                    
            except ValueError:
                return False

        def start_subprocess(self, event, decrypted_message, override=False):
            command = self.commands[event.public_key]
            iban = self.get_iban(event.public_key)
            email = self.get_email(event.public_key)
            if email is None or override:
                email = decrypted_message
            if iban is None or override:
                iban = decrypted_message            
            if command.command == "purchase" or command.command == "set_iban":
                self.show_iban_confirmation(event, iban, show_proceed=True)
            elif command.command == "set_email":
                self.show_email_confirmation(event, email, show_proceed=True)
            elif command.command == "swap":
                self.show_btc_address_confirmation(event, decrypted_message,)
            elif command.command == "confirm_address":
                self.show_signature_verified(event, command, decrypted_message)

        def show_provide_details(self, event):
            iban = self.get_iban(event.public_key)
            email = self.get_email(event.public_key)
            if email is None:
                self.show_provide_email(event)
            elif iban is None:
                self.show_provide_iban(event)

            if email is not None and iban is not None:
                self.show_proceed(event)

        def show_email_confirmation(self, event, decrypted_message, show_proceed=False):
            if decrypted_message and self.utils.validate_email(decrypted_message):
                self.set_email(event, decrypted_message)
                response = f"✔️ Email: {decrypted_message}"
                if show_proceed:
                    response += "\n\n/proceed to finalize the order.\n/cancel to cancel the order."
            else:
                response = "⚠️ Email is not valid. Please provide a valid email."
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=response)

        def show_iban_confirmation(self, event, decrypted_message, show_proceed=False):
            if decrypted_message and self.utils.validate_iban(decrypted_message):
                self.set_iban(event, decrypted_message)
                response = f"✔️ IBAN: {decrypted_message}"
                if show_proceed:
                    response += "\n\n/proceed to finalize the order.\n/cancel to cancel the order."
            else:
                response = "⚠️ IBAN is not valid. Please provide a valid IBAN."
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=response)

        # ON_CHAIN
        def show_btc_address_confirmation(self, event, decrypted_message):
            if decrypted_message and Utils.validate_btc_address(decrypted_message):
                self.set_btc_address(event, decrypted_message)
                response = f"✔️ Bitcoin address provided:\n\n{decrypted_message}\n\nUnder Swiss regulations, you must make a signature of the message below, using your wallet with mentioned address."
                response += "\n\n/verify to verify address.\n/cancel to cancel the order."
            else:
                response = "⚠️ BTC Address is not valid. Please provide a valid BTC Address."
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=response)

        # ON_CHAIN
        def show_confirm_address_ownership(self, event, message_to_sign):
            message = "Confirm address ownership.\n\nThe signature must be pasted below to proceed.\n\nMessage to sign: 👇"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            time.sleep(0.5)
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message_to_sign)

        # ON_CHAIN
        def show_signature_verified(self, event, command, signature):
            btc_address = self.get_btc_address(event.public_key)
            message = "⚠️ Signature verification failed. Please try again."
            message_to_sign = self.commands[event.public_key].message
            if message_to_sign and btc_address and signature:
                if signature and Utils.verify_signature(btc_address, signature, message_to_sign):
                    message = f"✔️ Signature Verified.\n\nAddress: {btc_address}"
                    self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
                    self.set_command(event, 'signature_verified', order_type=OrderType.ON_CHAIN, message=message_to_sign, signature=signature)
                    self.show_tiers(event, command, order_type=OrderType.ON_CHAIN)
            else:
                self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)

        # ON_CHAIN
        def get_challenge_token(self, event):
            res = self.api.create_challenge()
            if res:
                token = res['token'] # '2ff4575f'
                message_to_sign = self.settings.message_to_sign.replace('{token}', token)
                self.show_confirm_address_ownership(event, message_to_sign)
                self.set_command(event, 'confirm_address', order_type=OrderType.ON_CHAIN, message=message_to_sign)

        def show_welcome_message(self, event):
            display_name = self.get_display_name(event.public_key)
            name = self.get_name(event.public_key)
            message = ''
            if display_name is None:
                display_name = name
            if display_name is not None:
                message = f"💜 PV {display_name}!"
                self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            message = "⚡️🔗 BitcoinVoucherBot\n\nPure Nostr procedure. Enhanced privacy. Encrypted decentralized Bot running on Nostr.\n\n⚠️ Disclaimer: This Bot running on Nostr protocol which is in an early stage of development. Errors may occur.\n\n✅ Tested clients:\n- Snort\n- Iris\n- Coracle\n- Damus (iOS)\n- Amethyst (Android)"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            fee = self.api.get_fee()
            # message = f"Category description\n\nService: Denali\nType: ⚡️ Push to your Lighting Address\nCompanies: Accepted\nService Fee: {fee}%\nDelivery: upon payment received\n\n{self.quick_links}"
            message = f"{self.quick_links}"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            # reset previous command for this event
            self.reset_command(event)

        def show_disabled_message(self, event):
            message = "⚠️ Service is currently disabled. Please try again later.\n\nUse Telegram bot for now.\nhttps://t.me/BitcoinVoucherBot?start=19051303"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
        
        def show_cancel_message(self, event):
            if len(self.commands) > 0 and self.commands[event.public_key] is not None:
                last_order_id = self.get_last_order_id(event.public_key)
                if last_order_id:
                    ret = self.api.cancel_order(last_order_id)
                    if ret:
                        self.redis.hdel(event.public_key, "last_order_id")
                        message = f"✔️ ORDER CANCELLED.\n\nThe current order has been successfully cancelled. Do not pay on a cancelled order. For making a new order, please start the order procedure from the beginning.\n\n{self.quick_links}"
                        self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
                        self.reset_command(event)
                        return

            message = f"CANCELLED.\n\n{self.quick_links}"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            self.reset_command(event)

        def show_btc_price(self, event):
            price = self.api.get_price()
            price = "{:,}".format(price)
            message = f"BTC/EUR price is €{price}"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            self.reset_command(event)

        def show_tiers(self, event, command, order_type):
            if order_type == OrderType.LIGHTNING:
                lower = self.lightning_tiers[0]
                upper = self.lightning_tiers[1]
                message = f"Choose amount\nfrom: {lower} to: {upper} EUR.\n\n"
            elif order_type == OrderType.ON_CHAIN:
                if self.is_first_order(event):
                    lower = self.on_chain_tiers_first[0]
                    upper = self.on_chain_tiers_first[1]
                    message = f"⚠️ First order on-chain\n\n"
                    message += f"Choose amount\nfrom: {lower} to: {upper} EUR.\n\n"
                else:
                    lower = self.on_chain_tiers_others[0]
                    upper = self.on_chain_tiers_others[1]
                    message = f"Choose amount\nfrom: {lower} to: {upper} EUR.\n\n"

            message += f"/[amount] - choose amount 'e.g': /{lower+2}\n/cancel - cancel procedure"

            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            self.set_command(event, command, order_type=order_type)

        def show_purchase_service(self, event, command):
            message = f"Choose service you are interested in:\n\n/push ⚡️ Push Sats to your Lightning Address: /push\n/swap 🔗 Push Bitcoin to your on-chain address /swap \n/cancel cancel procedure: /cancel"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            self.reset_command(event)

        def show_purchase(self, event, command, type: OrderType):
            fee = self.api.get_fee()
            self.set_command(event, command, order_type=type)
            if type == OrderType.LIGHTNING:
                self.show_purchase_lightning(event, command, fee)
            elif type == OrderType.ON_CHAIN:
                self.show_purchase_on_chain(event, command, fee)
        
        def show_purchase_lightning(self, event, command, fee):
            # message = f"⚠️ Important. Due to exceptionally high Bitcoin onchain mining fees rate and high congestion of the mempool\n\nSome of our service has been paused until the mining fees are so high. You can make swap eur/bitcoin."
            message = f"Service description\n\nService: ⚡️ Push to your Lighting Address\nType: Push to your Lighting Address\nService Fee: {fee} %"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            self.show_tiers(event, command, order_type=OrderType.LIGHTNING)
        
        # ON_CHAIN
        def show_purchase_on_chain(self, event, command, fee):
            upper = self.on_chain_tiers_others[1]
            is_first_order = self.is_first_order(event)
            if is_first_order:
                upper = self.on_chain_tiers_first[1]
            limit_order_message = f"⚠️ First order on-chain\nfirst order: {upper} EUR/day.\nnext orders: 900 EUR/day." if is_first_order else "limit: 900 EUR/day."
            message = f"🔁 EUR/BTC Swap order.\n\nOnce the EUR payment arrives, you will receive the converted (swapped) amount in bitcoin to the address you provide.\n\n{limit_order_message}\n\nInstant sepa available: No\nService fee: {fee}%.\nProcessed: once per day"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            time.sleep(0.5)
            message = "Please paste the Bitcoin On-chain ₿ address you own in bech32 format (bc1q).\n/cancel - cancel procedure"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)

        def show_info(self, event):
            iban = self.get_iban(event.public_key)
            email = self.get_email(event.public_key)
            lud16 = self.get_lud16(event.public_key)
            message = "Info:\n\n"
            if iban:
                message += f"IBAN: {iban}\n"
            else:
                message += "IBAN: Not set\n"
            if email:
                message += f"Email: {email}\n"
            else:
                message += "Email: Not set\n"
            if lud16:
                message += f"Lightning Address: {lud16}\n"
            else:
                message += "Lightning Address: Not set\n"

            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)

        def show_tos(self, event):
            message = f"Terms of Service\n\n https://www.bitcoinvoucherbot.com/terms-of-service/"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
        
        def show_amount_confirmation(self, event, command, show_proceed=True):
            self.redis.hdel(event.public_key, "last_order_id")
            lud16 = self.get_lud16(event.public_key) if self.get_lud16(event.public_key) else "Not set"
            cmd = self.commands[event.public_key]
            service_type = "⚡️ Push to your Lightning Address" if cmd.order_type == OrderType.LIGHTNING else "🔗 Push Bitcoin to your on-chain address"
            recipient = lud16 if cmd.order_type == OrderType.LIGHTNING else self.get_btc_address(event.public_key)
            message = f"AMOUNT CHOSEN.\n\nYou chose to purchase\n\nAmount: {command} EUR\nService type: {service_type}\nRecipient: {recipient}\n\n{self.disclaimer}"
            if show_proceed:
                message += "\n\n/continue - accept and continue\n/cancel - cancel purchase"
            self.set_amount(event, int(command))
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
        
        def show_provide_iban(self, event, override_iban=False):
            iban = self.get_iban(event.public_key)
            if iban and override_iban is False:
                self.set_iban(event, iban)
                return
            
            self.set_iban(event, None)
            message = "⚠️ Please provide your IBAN.\n\nPlease provide your IBAN from your payment will come from.\n\nThis is required by the bank for faster payment management.\n\nDo not put extra characters in the IBAN string or wrong codes, to avoid procedure to abort."
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)

        def show_provide_email(self, event, override_email=False):
            email = self.get_email(event.public_key)
            if email and override_email is False:
                self.set_email(event, email)
                return
            
            self.set_email(event, None)
            message = "⚠️ Please provide your email.\n\nPlease provide your email from your payment will come from.\n\nThis is required by the bank for faster payment management.\n\nDo not put extra characters in the email string or wrong codes, to avoid procedure to abort."
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
        
        def show_support(self, event):
            pub_key = Utils.npub_from_hex(event.public_key) 
            message = self.support_message.replace('[pub_key]', pub_key)
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
        
        def show_stats(self, event):
            message = self.api.get_stats()
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
        
        def get_email(self, public_key):
            return str(self.redis.hget(public_key, 'email')).replace("b'", "").replace("'", "") if self.redis.hget(public_key, 'email') else None
        
        def get_iban(self, public_key):
            return str(self.redis.hget(public_key, 'iban')).replace("b'", "").replace("'", "") if self.redis.hget(public_key, 'iban') else None
        
        def get_last_order_id(self, public_key):
            return str(self.redis.hget(public_key, 'last_order_id')).replace("b'", "").replace("'", "") if self.redis.hget(public_key, 'last_order_id') else None
        
        def get_lud16(self, public_key):
            return str(self.redis.hget(public_key, 'lud16')).replace("b'", "").replace("'", "") if self.redis.hget(public_key, 'lud16') else None

        def get_display_name(self, public_key):
            return self.redis.hget(public_key, 'display_name').decode('utf-8') if self.redis.hget(public_key, 'display_name') else None

        def get_name(self, public_key):
            return self.redis.hget(public_key, 'name').decode('utf-8') if self.redis.hget(public_key, 'name') else None
        
        def get_nip05(self, public_key):
            return str(self.redis.hget(public_key, 'nip05')).replace("b'", "").replace("'", "") if self.redis.hget(public_key, 'nip05') else None
        
        def get_btc_address(self, public_key):
            return str(self.redis.hget(public_key, 'btc_address')).replace("b'", "").replace("'", "") if self.redis.hget(public_key, 'btc_address') else None
        
        def notify_payment(self, event):
            message = f"❌ ERROR.\n\n Ivalid order id.\n\n{self.quick_links}"
            last_order_id = self.get_last_order_id(event.public_key)
            lud16 = self.get_lud16(event.public_key)
            if last_order_id:
                ret = self.api.notify_payment(last_order_id)
                if ret:
                    message = f"👍 Payment notified.\n\nYour payment was notified and will be processed shortly.\n\nOrder ID: {last_order_id}\nRecipient: {lud16}\n\n{self.quick_links}"
            self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)

        def verify_admin(self, event):
            return event.public_key in self.settings.admins

        def show_proceed(self, event):
            date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
            cmd = self.commands[event.public_key] if event.public_key in self.commands else None
            order_type = cmd.order_type if cmd else None
            nip05 = self.get_nip05(event.public_key)
            if not nip05 and self.settings.nip05_verification:
                message = f"⚠️ Please configure a valid NIP05.\n\nEdit profile and add valid NIP05 than retry.\n\n/retry - to retry this step (make sure that you have filled missing params)\n\n{self.quick_links}"
                self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            elif cmd:
                message = self.error_message_proceed
                if cmd and cmd.command == 'purchase' or cmd.command == 'set_address' or cmd.command == 'set_iban' or cmd.command == 'signature_verified':
                    amount = self.amounts[event.public_key]
                    iban = self.get_iban(event.public_key)
                    email = self.get_email(event.public_key)
                    if amount and iban and email:
                        if order_type == OrderType.LIGHTNING:
                            self.create_order_lightning(event, amount, email, iban)
                        elif order_type == OrderType.ON_CHAIN:
                            self.create_order_on_chain(event, amount, email, iban)
                    else:
                        if email is None:
                            self.show_provide_email(event)
                            return
                        elif iban is None:
                            self.show_provide_iban(event)
                            return
                        else:
                            message = f"❌ ERROR.\n\nMissing amount.\n\n{self.quick_links}"
                            self.reset_command(event)

                        self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)
            else:
                self.send_message(recipient_pubkey=event.public_key, cleartext_content=self.error_message_proceed)

        def create_order_lightning(self, event, amount, email, iban):
            message = None
            # get user lud16
            lud16 = self.get_lud16(event.public_key)
            if lud16:
                res = self.api.create_lightning_order(amount, email, iban, event.public_key, lnaddress=lud16)
                if res:
                    result = Order(**res)
                    if result.call == "order.create_lightning":
                        if result.status.find(".accepted") > -1:
                            order_id = result.orderid
                            payment_reason = result.payment_description
                            date = result.order_time[0:4] + "-" + result.order_time[4:6] + "-" + result.order_time[6:8] + " " + result.order_time[8:10] + ":" + result.order_time[10:12]
                            creditor_name = result.payment_method.creditor_name
                            creditor_address = result.payment_method.creditor_address
                            creditor_bank_name = result.payment_method.creditor_bank_name
                            creditor_bank_iban = result.payment_method.creditor_bank_iban
                            creditor_bank_bic = result.payment_method.creditor_bank_bic
                            message = f"✔️ ORDER RECEIVED.\n\nDate: {date}\nAmount: {amount} EUR\nOrder type: ⚡️ Push to your Lightning Address\n\nSEPA Bank transfer coordinates\nBeneficiary: {creditor_name}\nAddress: {creditor_address}\n{creditor_bank_name} (BCN)\nIBAN: {creditor_bank_iban}\nBIC: {creditor_bank_bic}\nNet amount to pay: {amount} EUR\nPayment reason: {payment_reason}\n\nFrom IBAN: {iban}\n\nOrderid: {order_id}\nRecipient: {lud16}"
                            message += "\n\n/cancel to cancel the order.\n/notify to notify the payment."
                            self.redis.hset(event.public_key, 'last_order_id', order_id)
                        elif result.status == "recipient.invalid":
                            message = f"❌ ERROR.\n\Lightning address is not valid. Please edit profile and add lightning address than retry.\n\n{self.quick_links}"
                            self.reset_command(event)
                    else:
                        message = f"❌ ERROR.\n\nThere was an error with the order. Please try again.\n\n{self.quick_links}"
                        self.reset_command(event)
            else:
                message = f"❌ ERROR.\n\nMissing lightning address in your profile. Please edit profile and add lightning address than retry.\n\n/retry - to retry this step (make sure that you have filled missing params)\n\n{self.quick_links}"
                self.reset_command(event)
            
            if message:
                self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)

        # ON_CHAIN
        def create_order_on_chain(self, event, amount, email, iban):
            message = None
            btc_address = self.get_btc_address(event.public_key)
            cmd = self.commands[event.public_key]
            res = self.api.create_on_chain_order(btc_address, email, iban, cmd.signature, cmd.message, event.public_key)
            if res:
                result = Order(**res)
                if result.call == "order.create":
                    if result.status.find(".accepted") > -1:
                        order_id = result.orderid
                        payment_reason = result.payment_description
                        date = result.order_time[0:4] + "-" + result.order_time[4:6] + "-" + result.order_time[6:8] + " " + result.order_time[8:10] + ":" + result.order_time[10:12]
                        creditor_name = result.payment_method.creditor_name
                        creditor_address = result.payment_method.creditor_address
                        creditor_bank_name = result.payment_method.creditor_bank_name
                        creditor_bank_iban = result.payment_method.creditor_bank_iban
                        creditor_bank_bic = result.payment_method.creditor_bank_bic
                        message = f"✔️ ORDER RECEIVED.\n\nDate: {date}\nAmount: {amount} EUR\nOrder type: 🔗 Push Bitcoin to your on-chain address\n\nSEPA Bank transfer coordinates\nBeneficiary: {creditor_name}\nAddress: {creditor_address}\n{creditor_bank_name} (BCN)\nIBAN: {creditor_bank_iban}\nBIC: {creditor_bank_bic}\nNet amount to pay: {amount} EUR\nPayment reason: {payment_reason}\n\nFrom IBAN: {iban}\n\nOrderid: {order_id}\nRecipient: {btc_address}"
                        self.redis.hset(event.public_key, 'last_order_id', order_id)
                else:
                    message = f"❌ ERROR.\n\nThere was an error with the order. Please try again.\n\n{self.quick_links}"
                    self.reset_command(event)
            if message:
                self.send_message(recipient_pubkey=event.public_key, cleartext_content=message)

        def order_complete(self, payload):
            print(f"order_complete: {payload}")
            payload_json = json.loads(payload)['payload']
            order = OrderComplete(**payload_json)
            public_key_hex = PublicKey.from_npub(order.public_key).hex()
            if order.public_key:
                message = None
                if order.payment_hash != 'ERROR':
                    self.redis.hset(public_key_hex, 'last_order_id', order.orderid)
                    self.redis.rpush(public_key_hex + ":orders", order.orderid)
                    sats = order.sale_bitcoin * 100000000
                    message = f"✔️ ORDER COMPLETE.\n\nAmount: {order.fiat} EUR\nSATS: {sats} at: {order.price} EUR\n\nRecived at: {order.recipient}\nPayment hash: {order.payment_hash}\nOrder Id: {order.orderid}\nRecipient: {order.recipient}\n\n{self.quick_links}"
                    self.send_message(recipient_pubkey=public_key_hex, cleartext_content=message)
                    time.sleep(1)
                else:
                    message = f"❌ Something wrong has happened during the sending of Sats to your Lightning Address. Causes may be:\n\n- wrong Lightning Address\n- linked node down or unreachable\n- not enough liquidity or path not found\n\nSo please check your details. You can contact the support on telegram:\n\n- providing the correct Lightning Address\n- providing your public key (where the order originated)\n- providing the orderid"
                    self.send_message(recipient_pubkey=public_key_hex, cleartext_content=message)
                    time.sleep(1)
                    message = self.support_message.replace("[pub_key]", order.public_key)
                    self.send_message(recipient_pubkey=public_key_hex, cleartext_content=message)
                    time.sleep(1)
        
        def order_contact(self, payload):
            print(f"order_contact: {payload}")
            payload_json = json.loads(payload)['payload']
            orderid = payload_json['orderid']
            public_key = payload_json['public_key']
            public_key_hex = PublicKey.from_npub(public_key).hex()
            if public_key and orderid:
                message = f"⚠️ Action required\n\nPlease contact support at https://t.me/VoucherSupportBot on Telegram.\n\nYour order nr.\n{orderid}\n\nYour publick key is:\n{public_key}\n\nSome detail is necessary in order to process your order. Please act as soon as possible.\n\nThank you!"
                self.send_message(recipient_pubkey=public_key_hex, cleartext_content=message)
                time.sleep(1)