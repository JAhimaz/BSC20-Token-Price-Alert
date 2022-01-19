from urllib import request
from web3 import Web3
import requests
import json

def getReservePrice():

    web3 = Web3(Web3.HTTPProvider("https://bsc-dataseed.binance.org/"))

    with open('UniSwapPairABI.json') as json_file:
        data = json.load(json_file)

    abi = data["abi"]

    pair_contract = web3.eth.contract(address=Web3.toChecksumAddress("0x660876c86655882f106727fcabf5faed5a932d32"), abi=abi)

    (reserve0, reserve1, blockTimestampLast) = pair_contract.functions.getReserves().call()

    # Token reserve is reserve 0
    # Peg (BNB) reserve is reserve 1

    price = (float(reserve0) / 10 ** 9) / (float(reserve1) / 10 ** 18)

    return price

# print(reserve0, reserve1, blockTimestampLast)
# price = reserve1 / reserve0

# print(price)

# print(1 / (price / (10 ** (18 - 9))))