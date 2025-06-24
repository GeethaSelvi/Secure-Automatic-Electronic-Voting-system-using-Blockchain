from django.core.management.base import BaseCommand
from voter.models import Voter
from web3 import Web3

class Command(BaseCommand):
    help = 'Sync voter status with blockchain'
    
    def handle(self, *args, **options):
        w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
        contract_address = '0xYourContractAddress'
        contract_abi = [...]  # Your contract ABI
        
        contract = w3.eth.contract(address=contract_address, abi=contract_abi)
        
        for voter in Voter.objects.all():
            has_voted = contract.functions.voters(voter.eth_address).call()
            if has_voted:
                self.stdout.write(f'Clearing session for {voter.eth_address}')
                # Add logic to clear sessions if needed