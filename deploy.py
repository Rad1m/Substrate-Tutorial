import json
import os
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# In the video, we forget to `install_solc`
# from solcx import compile_standard
from solcx import compile_standard, install_solc

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

# We add these two lines that we forgot from the video!
print("Installing...")
install_solc("0.6.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"]
                }
            }
        },
    },
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

#get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

#get ABI
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

#for connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://0.0.0.0:8545"))
chain_id = 1337
my_address = "0xaddaddress"
private_key = os.getenv("PRIVATE_KEY") # never hard code a private key into any contract

# Create the contract in Python
SimpleStorage = w3.eth.contract(abi = abi, bytecode = bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# 1. Build a transaction
# 2. Sign a transaction
# 3. Send a transaction
transaction = SimpleStorage.constructor().buildTransaction({"chainID":chain_id, "from":my_address, "nonce":nonce})
signed_txn = w3.eth.account.sign_transaction(transaction, private_key = private_key) # never hard code a private key into any contract

# Send this signed transaction
print("Transaction executed...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
print("Waiting for transaction to finish...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash) # this will stop the code until thetransaction went through

# Working with the contract, you always need
# Contract Address
# Contract ABI
simple_storage = w3.eth.contract(address = tx_receipt.contractAddress, abi = abi)

# initial value of favourite number
print(simple_storage.functions.retrieve().call())
store_transaction = simple_storage.functions.store(15).buildTransaction({"chainId": chain_id, "from": my_address, "nonce": nonce+1})
signed_store_tx = w3.eth.account.sign_transaction(store_transaction, private_key)
send_store_tx = w3.eth.send_raw_transaction(signed_store_tx.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)