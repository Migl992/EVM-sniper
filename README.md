# EVM-sniper
# Sniper Bot for UniV2 Forks on EVMs
## About The Project

This project is a Sniper Bot designed to showcase the capabilities of interacting with EVMs and UniV2 forks. It's intended for educational purposes, allowing users to understand the mechanics behind automated trading and smart contract interactions. **Please note:** using this bot may result in financial loss. It's crucial to understand the risks involved and use it responsibly.

### Built With

- Python 3.8 or higher
- Web3.py library
- Go plus APIs

## What This Code Does

This code is built to interact with any UNIv2 fork on any EVM-compatible blockchain, with an example provided for the Fantom chain for SpookySwap. The bot performs several key actions to identify and potentially buy promising tokens:

- **Connect to the Chain:** Establishes a connection to the specified blockchain.
- **Listen for New Pair Creations:** Monitors the UNIv2 factory smart contract for the creation of new liquidity pairs.
- **Check Token Pairing:** Verifies if the newly created token is paired with the native coin of the chain (e.g., wFTM for Fantom).
- **Liquidity Check:** Assesses the liquidity of the new pair, allowing users to specify a minimum amount of the native coin (e.g., FTM) that must be present for the pair to pass the check.
- **Honeypot/Buy-Sell Tax/Slippage Check:** Simulates transactions on the chain interacting with a specific smart contract, assessing the risk of honeypot, buy-sell tax, and slippage. This step is crucial for identifying potential scams.(some scam token can bypass this check)
- **Call the GoPlus API:** Checks if the token is flagged as a honeypot by the GoPlus API. This step is only possible if the smart contract is verified, which is not always the case.
- **Deployer Flag Check:** Verifies if the contract deployer is flagged as a honeypot creator with goplus API.
- **Token Purchase:** If all checks pass, the bot proceeds to buy the token with the specified amount.
- **Telegram Notification:** All steps, including the purchase, are accompanied by a message sent to a Telegram bot, facilitating easy monitoring and management.


### Prerequisites

- Python 3.8 or higher
- Web3.py library
- An EVM wallet
- Your telegram bot

### How you can run this sniper

You can simply copy and paste and run the code in any python IDE, for example, Jupyter Notebook/Lab, or run it as Python script.

