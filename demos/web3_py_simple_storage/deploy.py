import json
import os
from solcx import compile_standard, install_solc
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

dir_path = os.path.dirname(os.path.realpath(__file__))

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    # print(simple_storage_file)

# Compile our solidity
install_solc("0.6.0")

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]}
            }
        },
    },
    solc_version="0.6.0",
)

# print(compiled_sol)

with open("./compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)

#----------------------------------------------------------------------------------
# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"][
    "bytecode"
]["object"]
# get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]
# To connect to rinkeby
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/98cf171ec14c49eb9e745010c5ad9876"))
chain_id = 4
my_address = "0xb5e6007a430C1629f0441d19E4C87B9AE35204B4"
private_key = os.getenv("PRIVATE_KEY")

#----------------------------------------------------------------------------------
# Create a contracte in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)
# Get the latest trancsaction
nonce = w3.eth.getTransactionCount(my_address)
# 1:Build a transaction
transaction = SimpleStorage.constructor().buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce}
)
# 2:Sign a transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
# 3:Send a transaction
print("Depoying contract...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# 4:Confirmation
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print("Depoyed!!!")
#----------------------------------------------------------------------------------

#Working with the contract:
#Contract Address
#Cojntract ABI
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

#initial value of favorite number
print(simple_storage.functions.retrieve().call())
print("Updating contract")
store_txn_storage = simple_storage.functions.store(15).buildTransaction(
    {"chainId": chain_id, "from": my_address, "nonce": nonce + 1}
)
signed_store_txn = w3.eth.account.sign_transaction(store_txn_storage, private_key)
send_stroe_txn = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
txn_receipt = w3.eth.wait_for_transaction_receipt(send_stroe_txn)
print("Updated!")

print(simple_storage.functions.retrieve().call())

#----------------------------------------------------------------------------------
