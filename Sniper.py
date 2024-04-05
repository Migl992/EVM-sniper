##################################################
#SPOOKY SWAP V2##################################
#################################################
import json
from web3 import Web3
import asyncio
import time
from telegram import Bot
from telegram.ext import Updater
from eth_abi import abi 
from decimal import Decimal
import requests
#################################################
#SETUP YOUR TELEGRAM BOT########################
#################################################
TOKEN = '7058355513:AAHZmhD8t3LkxUK9FhiJ4Q2Hbf5fFbeVXWA'
CHAT_ID = '21870468'
bot = Bot(token=TOKEN)
##################################################
ftm_ws = 'wss://wsapi.fantom.network/'
web3 = Web3(Web3.WebsocketProvider(ftm_ws))
print(web3.is_connected())

# Spookyswap Factory address and ABI
spooky_factory = 'factoryaddress' 
spooky_factory_abi = json.loads('FactoryABI')
contract = web3.eth.contract(address=spooky_factory, abi=spooky_factory_abi)
# Spookyswap Router address and ABI
spooky_router = 'routeraddress'
spooky_router_abi ='routerABI'
contractbuy = web3.eth.contract(address=spooky_router, abi=spooky_router_abi)

wFTM = web3.to_checksum_address('0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83') 
sender_address = web3.to_checksum_address('Yourwalletaddress') #test address
# Set up an event filter for the PoolCreated event
pair_created_filter = contract.events.PairCreated.create_filter(fromBlock='latest')

def check_liquidity(pair_address):
    pair_abi = 'uniV2pairABI' ##this will be the same for every pair
    wFTM_address = '0x21be370D5312f44cB42ce377BC9b8a0cEF1A4C83'
    
    pair_contract = web3.eth.contract(address=pair_address, abi=pair_abi)
    reserves = pair_contract.functions.getReserves().call()
    
    # Determine which token is WFTM in the pair
    token0 = web3.to_checksum_address(pair_contract.functions.token0().call())
    token1 = web3.to_checksum_address(pair_contract.functions.token1().call())
    
    if token0 == wFTM_address:
        reserveWFTM = reserves[0] / 10**18 # WFTM is token0
    elif token1 == wFTM_address:
        reserveWFTM = reserves[1] / 10**18 # WFTM is token1
    else:
        raise ValueError("WFTM not found in the pair")
    
    return reserveWFTM

def perform_honey_check(target_token_address, amount):
    # Initialize the contract
    sender_address = web3.to_checksum_address('YourAddress')
    spooky_router = 'Routeraddress'
    contract_abi = 'HOneycheckcontractABU' #you can find this in the github repor regarding the honeychaeck smart contract
    honey_check = web3.eth.contract(address='Honeychecksmartcontractaddress', abi=contract_abi)
    value = web3.to_wei(amount, 'ether')
    # Encode the function call
    data = honey_check.encodeABI(fn_name='honeyCheck', args=[target_token_address, spooky_router])
    
    # Get the gas price
    gas_price = web3.eth.gas_price
    
    # Attempt to make the call
    try:
        honey_tx_result = web3.eth.call({
            'from': sender_address,
            'to': 'Honeychecksmartcontractaddress',
            'gasPrice': gas_price,
            'value': value,
            'data': data
        })
        
        # Decode the response
        decodedABI = abi.decode(["uint256", "uint256", "uint256", "uint256", "uint256", "uint256"], honey_tx_result)
        
        # Extracting values
        buyGasCost = decodedABI[3]
        sellGasCost = decodedABI[4]
        buyResult = decodedABI[0]
        leftOver = decodedABI[1]
        sellResult = decodedABI[2]
        expectedAmount = decodedABI[5]
        
        # Calculations
        buyTax1 = float((1 - Decimal(buyResult) / Decimal(expectedAmount))) * 100
        sellTax1 = float((1 - Decimal(sellResult) / Decimal(value))) * 100
        sellTax = sellTax1 - buyTax1
        
        # Format the results to have only 3 decimal places
        buyTax = format(buyTax1, '.3f')
        sellTax = format(sellTax, '.3f')

        # Return the results
        result = {
            'buyTax': buyTax,
            'sellTax': sellTax,
            'buyGasCost': buyGasCost,
            'sellGasCost': sellGasCost,
            'isHoneypot': False, # Assuming the call was successful
        }
        
        return result
    except Exception as e:
        # If the call fails, return all values as 0 with isHoneypot as True
        print(f"Error occurred: {e}")
        return {
            'buyTax': 0,
            'sellTax': 0,
            'buyGasCost': 0,
            'sellGasCost': 0,
            'isHoneypot': True,
        }

def buy(tokenToBuy, amount):
    try:
        nonce = web3.eth.get_transaction_count(sender_address)

        # Build the transaction
        spookyswap_txn = contractbuy.functions.swapExactETHForTokens(
            0, # set to 0, or specify minimum amount of token you want to receive - consider decimals!!!
            [wFTM, tokenToBuy],
            sender_address,
            (int(time.time()) + 10000)
        ).build_transaction({
            'from': sender_address,
            'value': web3.to_wei(amount, 'ether'), # This is the Token(FTM) amount you want to Swap from
            'gasPrice': web3.to_wei('119', 'gwei'), # Manually set gas price or use  web3.eth.gas_price
            'nonce': nonce,
        })

        # Sign the transaction
        signed_txn = web3.eth.account.sign_transaction(spookyswap_txn, private_key='YOURPRIVATEKEY')############<- This is your private key, never share this with anyone, if someone get access to your P-key can control your wallet

        # Send the transaction
        tx_token = web3.eth.send_raw_transaction(signed_txn.rawTransaction)

        # Wait for the transaction to be mined
        tx_receipt = web3.eth.wait_for_transaction_receipt(tx_token)

        print("Snipe was successful, bought: " + web3.to_hex(tx_token))
        print("Transaction hash: ", tx_receipt)

    except Exception as e:
        print(f"An error occurred: {e}")

def buy_new_listing(amount):
    while True:
        new_events = pair_created_filter.get_new_entries()
        for event in new_events:
            token0 = web3.to_checksum_address(event['args']['token0'])
            token1 = web3.to_checksum_address(event['args']['token1'])
            pair = web3.to_checksum_address(event['args']['pair'])
            
            # Check if either token0 or token1 is wFTM
            if token0 == wFTM or token1 == wFTM:
                message = f"New pair created with WFTM: {token0} - {token1} at address {pair}"
                print(message)
                bot.send_message(chat_id=CHAT_ID, text=message)
                
                # Determine the token not paired with WFTM
                token_to_buy = token1 if token0 == wFTM else token0
                
                # Start checking liquidity for 3 minutes (180 seconds)
                start_time = time.time()
                liquidity_check_success = False
                tentative = 1
                while time.time() - start_time < 180: # 3 minutes
                    liquidity = check_liquidity(pair)
                    print(f"\rTentative {tentative}: Checking liquidity for pair {pair}: {liquidity}", end='', flush=True)
                    if liquidity > 3000:   ########################################################### <- Specify here the minimum amount of liquidity you want to be OK
                        liquidity_check_success = True
                        break
                    tentative += 1
                    time.sleep(5) # Check every 5 seconds
                
                if liquidity_check_success:
                    # Perform honey check after liquidity check
                    honey_check_result = perform_honey_check(token_to_buy, amount)
                    messagehoney = f"Honey check results: {honey_check_result}"
                    print(messagehoney)
                    bot.send_message(chat_id=CHAT_ID, text=messagehoney)

                    # Perform API call check
                    api_url = f"https://api.gopluslabs.io/api/v1/token_security/250?contract_addresses={token_to_buy}"
                    response = requests.get(api_url)
                    if response.status_code == 200:
                        data = response.json()
                        token_data = data['result'].get((token_to_buy).lower(), {})
                        is_honeypot = token_data.get('is_honeypot', "0")
                        honeypot_with_same_creator = token_data.get('honeypot_with_same_creator', "0")
                        
                        if is_honeypot == "1" or honeypot_with_same_creator == "1":
                            print(f"API check failed for pair {pair}, token not bought")
                            bot.send_message(chat_id=CHAT_ID, text=f"API check failed for pair {pair}, token not bought")
                            continue # Skip the rest of the loop for this iteration
                    

                    # Check if honey check is not a honeypot and taxes are less than 10
                    if not honey_check_result['isHoneypot'] and float(honey_check_result['buyTax']) < 10 and float(honey_check_result['sellTax']) < 10:
                        buy(token_to_buy, amount)
                        print(f"i have bought token {token_to_buy}")
                        bot.send_message(chat_id=CHAT_ID, text=f"i have bought token {token_to_buy}")
                    else:
                        print(f"Honey check failed for pair {pair}, token not bought")
                        bot.send_message(chat_id=CHAT_ID, text=f"Honey check failed for pair {pair}, token not bought")
                else:
                    print(f"Liquidity check failed for pair {pair}")
                    bot.send_message(chat_id=CHAT_ID, text=f"Liquidity check failed for pair {pair}, token not bought")
        time.sleep(2) # Poll every 2 seconds
