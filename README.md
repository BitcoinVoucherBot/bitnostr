[![Deploy](https://github.com/BitcoinVoucherBot/bitnostr/actions/workflows/deploy.yml/badge.svg?branch=main)](https://github.com/BitcoinVoucherBot/bitnostr/actions/workflows/deploy.yml)

# ⚡️🔗 BitcoinVoucherBot

Welcome to the BitcoinVoucherBot repository! We're excited to share our user-friendly, privacy-focused tool that simplifies the process of swapping your Bitcoin. Built on the innovative [Nostr](https://github.com/nostr-protocol/nostr) protocol, our bot offers an exceptional experience while keeping your transactions secure.

## 🌟 Key Features
- Intuitive commands for a seamless user experience.
- Push Sats to your Lightning Address or swap Bitcoin to your on-chain address.
- Detailed step-by-step guidance throughout the swapping process.
- Strong focus on privacy with encrypted and decentralized architecture.
- Compatible with a variety of [Nostr](https://github.com/nostr-protocol/nostr) clients.

## 📚 Prerequisities

In order to run this container you'll need docker installed.

* [Windows](https://docs.docker.com/windows/started)
* [OSX](https://docs.docker.com/mac/started/)
* [Linux](https://docs.docker.com/linux/started/)

## 👨‍💻 Usage

1. Request a [BitcoinVoucherBot API key and BOT API key](https://t.me/BitcoinVoucherGroup)

2. Chekout the code from GitHub

```bash
git clone https://github.com/BitcoinVoucherBot/bitnostr.git
```

3. Rename ```settings.tpl.json``` into ```settings.json``` and fill missing required fields :
    * ```nostr_private_key```: Your Nostr bot private key
    * ```nostr_public_key```: Your Nostr bot public key
    * ```bvb_api_key```: Your BitcoinVoucherBot API key 
    * ```bot_api_key```: Your Bot API key

4. Run the docker compose

```bash
docker compose up -d --build
```

## 🔍 Implemented NIPs (Nostr Implementation Possibilities)

* [NIP-01: Basic protocol flow description](https://github.com/nostr-protocol/nips/blob/master/01.md)
* [NIP-04: Encrypted Direct Message](https://github.com/nostr-protocol/nips/blob/master/04.md)
* [NIP-05: Mapping Nostr keys to DNS-based internet identifiers](https://github.com/nostr-protocol/nips/blob/master/05.md)

## ✅ Tested clients

* [Snort](https://snort.social)
* [Iris](https://iris.to)
* [Coracle](https://coracle.social)
* [Damus (iOS)](https://damus.io)
* [Amethyst (Android)](https://play.google.com/store/apps/details?id=com.vitorpamplona.amethyst)

## 📖 HOWTO

For a complete user's guide on how to use the BitcoinVoucherBot, please check out our [step-by-step guide](./HOWTO.md).
## 💼 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## ⚠️ Disclaimer

This Bot running on Nostr protocol which is in an early stage of development.

* It might have some bugs.
* It need more tests.

We welcome your feedback and suggestions! If you have any questions or need assistance, please feel free to create an issue, add PRs, or provide any feedback!
