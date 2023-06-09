#!/usr/bin/env python3

import time
import math
import json
from nostr.nostr.key import PrivateKey, PublicKey

class Settings:

    # fields
    ENABLED = "enabled"
    PRIVATE_KEY = "nostr_private_key"
    PUBLIC_KEY = "nostr_public_key"
    RELAYS = "relays"
    LAST_MESSAGE_CREATED_AT = "last_message_created_at"
    BVB_API_KEY = "bvb_api_key"
    LIGHTNING_TIERS = "lightning_tiers"
    BOT_API_KEY = "bot_api_key"
    NIP05_VERIFICATION = "nip05_verification"
    ADMINS = "admins"
    MESSAGE_TO_SIGN = "message_to_sign"
    ON_CHAIN_TIERS = "on_chain_tiers"

    def __init__(self):
        # read settings.json
        with open("settings.json", "r") as f:
            self._settings = json.load(f)
        
        self.set_last_message_created_at(math.floor(time.time()))

    @property
    def enabled(self) -> bool:
        return self._settings.get(Settings.ENABLED)

    @property
    def private_key(self) -> PrivateKey:
        return PrivateKey.from_nsec(self._settings.get(Settings.PRIVATE_KEY))

    @property
    def private_key_hex(self) -> PublicKey:
        return self.private_key.hex()

    @property
    def public_key(self) -> PublicKey:
        return PublicKey.from_npub(self._settings.get(Settings.PUBLIC_KEY))

    @property
    def public_key_hex(self) -> PublicKey:
        return self.public_key.hex()
    
    @property
    def relays(self) -> list:
        return self._settings.get(Settings.RELAYS)

    @property
    def last_message_created_at(self) -> int:
        return self._settings.get(Settings.LAST_MESSAGE_CREATED_AT)
    
    @property
    def bvb_api_key(self) -> str:
        return self._settings.get(Settings.BVB_API_KEY)
    
    @property
    def lightning_tiers(self) -> list:
        return self._settings.get(Settings.LIGHTNING_TIERS)
    
    @property
    def on_chain_tiers_first(self) -> list:
        on_chain_tiers = self._settings.get(Settings.ON_CHAIN_TIERS)
        return on_chain_tiers.get("first")
    
    @property
    def on_chain_tiers_others(self) -> list:
        on_chain_tiers = self._settings.get(Settings.ON_CHAIN_TIERS)
        return on_chain_tiers.get("others")

    @property
    def bot_api_key(self) -> str:
        return self._settings.get(Settings.BOT_API_KEY)
    
    @property
    def nip05_verification(self) -> bool:
        return self._settings.get(Settings.NIP05_VERIFICATION)
    
    @property
    def admins(self) -> list:
        ret = [PublicKey.from_npub(admin).hex() for admin in self._settings.get(Settings.ADMINS)]
        return ret
    
    @property
    def message_to_sign(self) -> str:
        return self._settings.get(Settings.MESSAGE_TO_SIGN)

    def set_last_message_created_at(self, message_created_at: int):
        self._settings[Settings.LAST_MESSAGE_CREATED_AT] = message_created_at
        self.save()
    
    def set_relays(self, relays: list):
        self._settings[Settings.RELAYS] = relays
        self.save()

    def set_enabled(self, enabled: bool):
        self._settings[Settings.ENABLED] = enabled
        self.save()

    def save(self):
        with open("settings.json", "w") as f:
            json.dump(self._settings, f, indent=4)
