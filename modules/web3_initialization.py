
from web3 import Web3

class Web3Initializer:
    #The OVM endpoint allows us to interact with the contract via web3
    def __init__(self, ovm_endpoint):
        # Connect to the Optimism OVM endpoint
        self.web3 = Web3(Web3.HTTPProvider(ovm_endpoint))