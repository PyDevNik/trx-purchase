from config import EXCHANGE, TRANSACTIONS_URL, RECEIVER_ADDRESS
import requests

def get_transaction(user_address):
    r = requests.get(TRANSACTIONS_URL.format(RECEIVER_ADDRESS))
    data = r.json()["data"]
    addresses = [transaction["from"] for transaction in data]
    address = addresses.index(user_address)
    if user_address != addresses[address]:
        return
    amount = data[address]["value"]
    return amount