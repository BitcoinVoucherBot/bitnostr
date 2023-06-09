# 📖 BitcoinVoucherBot: A step-by-step guide

A user-friendly, privacy-focused, decentralized BitcoinVoucherBot's interface that runs on the Nostr protocol as a Direct messages Bot. Communication between the Nostr bot and the user is E2E encrypted (please see NIP-04). Follow these simple steps to start swapping your Bitcoin with enhanced privacy and security:

## Table of Contents
- [Getting Started](#getting-started)
- [Setting Your Email](#setting-your-email)
- [Registering Your IBAN](#registering-your-iban)
- [Checking Your Details](#checking-your-details)
- [Choosing Your Action](#choosing-your-action)
- [Push Procedure](#push-procedure)
- [Swap Procedure](#swap-procedure)
- [Cancel Procedure](#cancel-procedure)
- [Additional Commands](#additional-commands)

## Getting Started

1. Search for `npub1fwcucd29vzleqlu8zjrs7dxpmurujgrk3yu2vtq6usx4wfspxjeqyw5089` in a Nostr client.

2. Open DM and type `/start` to kick off a new procedure with the bot.

## Setting Your Email
3. Use the `/email` command to provide your email address for notifications in case of need. Please note that otherwise no email is sent.

## Registering Your IBAN
4. Enter your bank account's IBAN using the `/iban` command. This is needed by target bank during the process to match the incoming payment.

## Checking Your Details
5. Use `/info` to view your current email, IBAN, and other details.

## Choosing Your Action
6. Choose between `/push` or `/swap`:
   - `/push`: Start the procedure to push Sats to your Lightning Address (as defined in your Nostr profile).
   - `/swap`: Begin the process of pushing Bitcoin to your external on-chain address.

Both procedures are non-custodial.

## Push Procedure
Follow these steps for `/push` (to Lightning Address):

1. Type `/push` to start the process.
2. Select the desired amount (e.g., `/54`; limit: 50 - 200).
3. Continue with `/continue` and verify the order details.
4. Make a wire transfer to the provided bank IBAN.
5. Notify the bot with `/notify` once the payment is done.
6. Wait for the Sats to be pushed to your Lightning Address.

💡 Remember to make the payment from the registered IBAN and use the provided orderId as the description.

## Swap Procedure
Follow these steps for `/swap`:

1. Type `/swap` to start the process.
2. Paste your Bitcoin on-chain address (bech32 format, e.g., bc1q).
3. Use `/verify` to begin the address verification process.
4. Sign the confirmation message using your Bitcoin wallet.
5. Select the desired amount (e.g., `/54`; limit: 50 - 200 for first order, 200 - 900 for others).
6. Continue with `/continue` and verify the order details.
7. Make a wire transfer to the provided bank IBAN.
8. Wait for the Sats to be pushed to your on-chain address.

💡 Remember to make the payment from the registered IBAN and use the provided orderId as the description.

## Cancel Procedure
- Type `/cancel` at any time to stop the current procedure.

## Additional Commands
- Use `/help` for a helpful guide, `/tos` for Terms of Service, and `/support` for support channels.
- Type `/stats` for current miner fees and `/price` for the BTC/EUR price.

Now that you know the steps, go ahead and enjoy swapping your Bitcoin with enhanced privacy and security using BitcoinVoucherBot! 🎉
