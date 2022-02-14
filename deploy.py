from itertools import chain
from solcx import compile_standard , install_solc
import json
from web3 import Web3
import os
from dotenv import load_dotenv
load_dotenv()
from web3.middleware import geth_poa_middleware


with open("./simplestorage.sol") as file:
    simple_storage_file = file.read()
    

install_solc("0.8.0")   
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol" : {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
            }
        },
    },
    solc_version="0.8.0",
)

with open("compiled_code.json" , 'w') as file:
    json.dump(compiled_sol , file) 
    
    
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]


w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/491566110c52493197254882991740a3"))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
chain_id = 4    
my_address = "0xb02a3Aa19660d104CfC15325fC6ea7b5007bbE61"

private_key = os.getenv("PRIVATE_KEY")

SimpleStorage = w3.eth.contract(abi = abi , bytecode= bytecode)

nonce = w3.eth.getTransactionCount(my_address)

transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId":chain_id, "from" : my_address , "nonce" : nonce})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key= private_key)
print("deploying contract")


tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("deployed!")


simple_storage = w3.eth.contract(address=tx_receipt.contractAddress , abi=abi)
print(simple_storage.functions.retrieve().call())
print("updating contract")

store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId":chain_id, "from" : my_address , "nonce" : nonce + 1})
signed_store_txn = w3.eth.account.sign_transaction(store_transaction , private_key = private_key)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt= w3.eth.wait_for_transaction_receipt(send_store_tx)
print("updated!")
print(simple_storage.functions.retrieve().call())
