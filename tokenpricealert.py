from distutils.log import debug
import os
import logging
import json
from logging.handlers import RotatingFileHandler
from dotenv.main import load_dotenv
import requests
from datetime import timedelta
import time
from pythonpancakes import PancakeSwapAPI

from web3 import Web3

from uniswapv2 import getReservePrice

load_dotenv()
ps = PancakeSwapAPI()

SIGNIFICANT_PERCENTAGE = 0.05

CURRENT_PRICE = None

def configureLogging():
    logFormatter = logging.Formatter("%(levelname)s - %(asctime)s --> %(message)s")

    fileHandler = RotatingFileHandler("/home/app/logs/output.log", mode="a+", maxBytes=10*1024*1024, backupCount=3)
    fileHandler.setFormatter(logFormatter)
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(logFormatter)

    log = logging.getLogger()
    log.setLevel(logging.INFO)
    log.addHandler(streamHandler)
    log.addHandler(fileHandler)

def priceAlert(token):
    global CURRENT_PRICE

    bnbData = ps.tokens(BNB_ADD)
    bnbPrice = bnbData['data']['price']

    token_balance = round(float(token.functions.balanceOf(WALLET_ADD).call()) / (10 ** int(DECIMALS)), 2)

    tokenPERBNB = getReservePrice()
    price = float(bnbPrice) / float(tokenPERBNB)

    currentBalanceValue = token_balance * price
    # print(f'${round(currentBalanceValue, 2)}')

    if(CURRENT_PRICE == None):
        CURRENT_PRICE = price

    # print(f'OLD PRICE: {CURRENT_PRICE}\nNEW PRICE: {price}')

    if(not CURRENT_PRICE == None and not CURRENT_PRICE == price):
        # MARGINUP = CURRENT_PRICE + (CURRENT_PRICE * 0.02)
        # MARGINDOWN = CURRENT_PRICE - (CURRENT_PRICE * 0.02)

        if(price >= CURRENT_PRICE):

            percentage = ((price - CURRENT_PRICE) / CURRENT_PRICE) * 100

            data = {
                'wallet_balance' : token_balance,
                'price_change' : 'UP',
                'token_price' : price,
                'price_change_percentage' : percentage,
                'wallet_balance_usd' : round(currentBalanceValue, 2)
            }

            CURRENT_PRICE = price
            return data

        if(price <= CURRENT_PRICE):

            percentage = ((CURRENT_PRICE - price) / price) * 100

            data = {
                'wallet_balance' : token_balance,
                'price_change' : 'DOWN',
                'price_change_percentage': percentage,
                'token_price' : price,
                'wallet_balance_usd' : round(currentBalanceValue, 2)
            }

            CURRENT_PRICE = price
            return data

        return False

API_TELEGRAM = f'https://api.telegram.org/bot{os.getenv("TG_API_KEY")}/sendMessage'
API_KEY_BSC = os.getenv('API_KEY_BSC')
WALLET_ADD = os.getenv('WALLET_ADD')
BNB_ADD = os.getenv("BNB_ADD")
TOKEN_ADD = os.getenv("TOKEN_ADD")
CHECKSUM_TOKEN_ADD = Web3.toChecksumAddress(TOKEN_ADD)
DECIMALS = os.getenv("DECIMALS")

TOKEN_ABI_URL = f"https://api.bscscan.com/api?module=contract&action=getabi&address={TOKEN_ADD}&apikey={API_KEY_BSC}"

# Pre-requisite Check
web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))
if(web3.isConnected()):
    logging.info("[Connected to Web3 Services]")
    # print("[Connected to Web3 Services]")

    response = requests.get(TOKEN_ABI_URL).json()
 
    if(response):
        abi = json.loads(response['result'])
        
        logging.info("[ABI Contract has been recieved]")
        # print("[ABI Contract has been recieved]")

        token = web3.eth.contract(address=CHECKSUM_TOKEN_ADD, abi=abi) # declaring the token contract

        while True:
            data = priceAlert(token)

            if(not data):
                logging.info("[No Price Changes]")
                # print("No Changes")
            else:

                if(data['price_change'] == "UP"):
                    emoji = "🟢"
                elif(data['price_change'] == "DOWN"):
                    emoji = "🔴"
                else:
                    emoji = "❌"
                
                message = f'''

{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}

🏦 TOKEN PRICE: ${round(data['token_price'], 7)}

💰 YOUR TOKENS: {data['wallet_balance']}
💴 YOUR BALANCE (USD): ${data['wallet_balance_usd']}

〽️ PRICE CHANGE: {data['price_change']}
📈 PRICE CHANGE (%): {round(data['price_change_percentage'], 3)}%

{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}{emoji}
                '''

                data = {
                    'chat_id': -1001749352065,
                    'parse_mode': 'HTML',
                    'text': message,
                    'disable_web_page_preview': True,
                }

                if(round(data['price_change_percentage'], 3) > SIGNIFICANT_PERCENTAGE):
                    telegramPost = requests.post(API_TELEGRAM, data).json()
                else:
                    logging.info("[Price Change not Significant]")

            time.sleep(5)
else:
    logging.warning("[Failed to Connect to Web3 Services]")
    # print("[Failed to Connect to Web3 Services]")



