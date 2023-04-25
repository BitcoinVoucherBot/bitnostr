#!/usr/bin/env python3

import json 
import ssl
import time
import math
from typing import List, Tuple
from nostr.nostr.filter import Filter, Filters
from nostr.nostr.event import Event, EventKind
from nostr.nostr.relay_manager import RelayManager
from nostr.nostr.message_type import ClientMessageType
from nostr.nostr.key import PublicKey

from ..settings import Settings

class NostrCoreBot:
     
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        
        self.ssl_options = {"cert_reqs": ssl.CERT_NONE}
        self.settings = Settings()
        self.setup()

    def setup(self):
        self.relay_manager = RelayManager()
        self.relay_manager.on_relay_open = self.on_relay_open

    def on_relay_open(self, url):
        print(f"RELAY CONNECTED - {url}")
        self.subscribe_to_direct_messages(url=url)
    
    def on_relay_close(self, url):
        print(f"RELAY DISCONNECTED - {url}")
    
    def update(self):
        messages = self.get_messages()
        if  messages is not None:
            for event, cleartext in messages:
                if event.kind == EventKind.SET_METADATA:
                    self.process_metadata(event=event, metadata=cleartext)
                else:   
                    if cleartext:
                        self.process_message(event=event, decrypted_message=cleartext)

    def get_messages(self) -> List[Tuple[Event,str]]:
        messages = {}
        responded = []
        while self.relay_manager.message_pool.has_events():
            event_msg = self.relay_manager.message_pool.get_event()
            url = event_msg.url
            event = event_msg.event
            subscription_id = event_msg.subscription_id

            if event.kind == EventKind.TEXT_NOTE:
                continue
            
            if event.public_key == self.settings.public_key_hex and len(event.tags) > 0:
                responded.append(event.tags[0])
                continue
            
            try:
                print(f"From {event.public_key}: {event.content} | created_at: {event.created_at} | event_id: {event.id} | from {url}")
                cleartext = None
                if event.kind == EventKind.SET_METADATA:
                    json_content = json.loads(event.content)
                    json_content['url'] = url
                    json_content['created_at'] = event.created_at
                    cleartext = json_content
                if event.kind == EventKind.ENCRYPTED_DIRECT_MESSAGE:
                    cleartext = self.settings.private_key.decrypt_message(encoded_message=event.content, public_key_hex=event.public_key)
            except ValueError:
                # The relays returned a DM that references us in a 'p' tag but is encrypted for someone else!
                print(f"Ignoring event_id {event.id} from {event.public_key}; can't decrypt")
                continue
            except Exception as e:
                print(e)
                continue

            if event.public_key not in messages or messages[event.public_key]["event"].created_at < event.created_at:
                # Update to the more recent Event
                if cleartext:
                    print(f"Latest from {event.public_key}: {event.id} ({event.created_at})")
                    messages[event.public_key] = dict(event=event, cleartext=cleartext)

            print(f"{event.public_key}: {cleartext}")

            if messages:
                print(messages)
            if responded:
                print(responded)

            # Have we already responded to any of these messages?
            try:
                for event_id in responded:
                    for pubkey, dm_dict in messages.items():
                        if dm_dict["event"].id == event_id and event.kind != EventKind.SET_METADATA:
                            print(f"Already responded to {pubkey} / {event_id}")
                            dm_dict["has_responded"] = True
                            break
            except Exception as e:
                import traceback, sys
                traceback.print_exc(file=sys.stdout)
            
            return [(d["event"], d["cleartext"]) for d in messages.values() if "has_responded" not in d]
        
    def process_message(self, event: Event, decrypted_message: str):
        # override this method in your bot class
        pass

    def process_metadata(self, event: Event, metadata: dict):
        # override this method in your bot class
        pass

    def set_last_message_created_at(self, event: Event):
        if self.settings.last_message_created_at is None or self.settings.last_message_created_at < event.created_at:
            print(f"Updating last_message_created_at to {event.created_at}")
            self.settings.set_last_message_created_at(event.created_at)

    def send_message(self, recipient_pubkey: str, cleartext_content: str):

        encrypted_message = self.settings.private_key.encrypt_message(message=cleartext_content, public_key_hex=recipient_pubkey)

        event = Event(public_key=self.settings.public_key_hex, 
                        content=encrypted_message, 
                        kind=EventKind.ENCRYPTED_DIRECT_MESSAGE,
                        tags=[["p", recipient_pubkey]])

        self.settings.private_key.sign_event(event=event)

        message = event.to_message()
        print('Sending message: ' + message)
        
        self.relay_manager.publish_event(event=event)
        time.sleep(1) # allow the messages to send

    def connect_relays(self, relays=None):
        relays_to_connect = self.settings.relays
        if relays is not None:
            relays_to_connect = relays[:50]
        
        for relay in self.settings.relays:
            if relay not in relays_to_connect:
                relays_to_connect.append(relay)

        self.relay_manager.stop_threads = False
        for relay in relays_to_connect:
            self.relay_manager.add_relay(relay)

    def subscribe_to_direct_messages(self, url):
        since = self.settings.last_message_created_at
        if since is None:
            since += 1
        
        filters = Filters([
            # messages sent to this nostr bot...
            Filter(pubkey_refs=[self.settings.public_key_hex], kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE], since=self.settings.last_message_created_at),
            # ...and messages sent from this nostr bot
            Filter(authors=[self.settings.public_key_hex], kinds=[EventKind.ENCRYPTED_DIRECT_MESSAGE], since=self.settings.last_message_created_at),
        ])

        # random string that should be used to represent a subscription
        seed = math.floor(time.time())
        subscription_id = "sub-{seed}".format(seed=seed)
        request = [ClientMessageType.REQUEST, subscription_id]
        json_filters = filters.to_json_array()
        print(f"Sending subscription request with filters {json_filters} to: {url}")
        request.extend(json_filters)

        # self.relay_manager.add_subscription_on_all_relays(subscription_id, filters=filters)
        self.relay_manager.add_subscription_on_relay(url, subscription_id, filters=filters)
        time.sleep(1) # allow the messages to send
    
    def disconnect_relays(self):
        pass   

    def get_profile(self, public_key: str):
        if 'npub' in public_key:
            public_key = PublicKey.from_npub(public_key).hex()
        filters = Filters([
            Filter(authors=[public_key], kinds=[EventKind.SET_METADATA], limit=1), # , until=int(time.time())
        ])
        seed = math.floor(time.time())
        # subscription_id = "{pub_key}-{seed}".format(pub_key=event.public_key, seed=seed)
        subscription_id = "profile-{seed}".format(seed=seed)
        request = [ClientMessageType.REQUEST, subscription_id]
        json_filters = filters.to_json_array()
        print(f"Sending profile request for {public_key} with filters {json_filters}")
        request.extend(json_filters)
        self.relay_manager.add_subscription_on_all_relays(subscription_id, filters=filters)

    async def get_notes(self, public_key: str, limit=15):
        if 'npub' in public_key:
            public_key = PublicKey.from_npub(public_key).hex()
        filters = Filters([
            Filter(authors=[public_key], kinds=[EventKind.TEXT_NOTE], until=int(time.time()), limit=limit)
        ])
        seed = math.floor(time.time())
        # subscription_id = "{pub_key}-{seed}".format(pub_key=event.public_key, seed=seed)
        subscription_id = "notes-{seed}".format(seed=seed)
        request = [ClientMessageType.REQUEST, subscription_id]
        json_filters = filters.to_json_array()
        print(f"Sending notes request for {public_key} with filters {json_filters}")
        request.extend(json_filters)
        if len(self.relay_manager.relays) > 0:
            self.relay_manager.add_subscription_on_all_relays(subscription_id, filters=filters)

            notes = []
            while True:
                while self.relay_manager.message_pool.has_events() or self.relay_manager.message_pool.has_eose_notices():
                    event_msg = None
                    eose_notice = None
                    if self.relay_manager.message_pool.has_events():
                        event_msg = self.relay_manager.message_pool.get_event()
                    if self.relay_manager.message_pool.has_eose_notices():
                        eose_notice = self.relay_manager.message_pool.get_eose_notice()

                    if event_msg is not None:
                        event = event_msg.event

                        if event.kind == EventKind.TEXT_NOTE:
                            print(f"Got note from {event.public_key}: {event.content}")
                            notes.append(event.content)

                    if eose_notice and eose_notice.subscription_id == subscription_id:
                        print(f"Got eose notice for {subscription_id}")
                        return notes
        else:
            return ["No relays connected"]