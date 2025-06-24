# vo/voting/voter/blockchain.py
from web3 import Web3
from django.conf import settings

def get_web3():
    w3 = Web3(Web3.HTTPProvider(settings.WEB3_PROVIDER_URL))
    return w3

def get_contract():
    w3 = get_web3()
    contract = w3.eth.contract(
        address=settings.CONTRACT_ADDRESS,
        abi=settings.CONTRACT_ABI
    )
    return contract