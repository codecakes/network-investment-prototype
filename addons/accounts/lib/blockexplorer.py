import requests
from urllib2 import urlparse
from functools import wraps

ether_key = "6F98VB1ZJ6MY46JHZ9AVR6YJQJPU3RCH95"

coins = {
    "btc": {
        "host": "https://blockexplorer.com/",
        "txn_api": "api/tx/",
        "addr_api": "api/addr/"
    },
    "eth": {
        "host": "https://api.etherscan.io",
        "txn_api": "api?module=transaction&action=gettxreceiptstatus&apikey=6F98VB1ZJ6MY46JHZ9AVR6YJQJPU3RCH95" # txhash=0x513c1ba0bebf66436b5fed86ab668452b7805593c05073eb2d51d3a52f480a76&
        # "addr_api":
    },
    "xrp": "https://data.ripple.com"
}


def get_endpoints(addr, txn_id, coin):
    api_host = coins.get(coin)
    if coin == "btc":
        txn_endpoint = "api/tx/%s" % (txn_id)
        coin_endpoint = "api/addr/%s" % (addr)
    elif coin == "eth":
        txn_endpoint = "api?module=transaction&action=gettxreceiptstatus&txhash=%s&apikey=6F98VB1ZJ6MY46JHZ9AVR6YJQJPU3RCH95" %(txn_id) #
        coin_endpoint = "api?module=account&action=txlist&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=6F98VB1ZJ6MY46JHZ9AVR6YJQJPU3RCH95" %(addr) % (addr)
    # elif coin == "xrp":
    #     txn_endpoint = "api/tx/%s" % (txn_id)
    #     coin_endpoint = "api/addr/%s" % (addr)
    txn_api = urlparse.urljoin(api_host, txn_endpoint)
    addr_api = urlparse.urljoin(api_host, coin_endpoint)
    return [txn_api, addr_api]

def validate_transaction(addr, txn_id, coin="btc"):
    api_host = coins.get(coin)
    txn_api, addr_api = get_endpoints(addr, txn_id, coin)

    txn_res = requests.get(txn_api)
    addr_res = requests.get(addr_api)

    if coin == "btc":
        if txn_res and addr_res:
            j_txn = txn_res.json()
            j_addr = addr_res.json()
            addresses = [each['addr'] if each.get('addr') else None for each in j_txn["vin"]] + reduce(lambda x, y: x + y,
                                                                         [each['scriptPubKey']['addresses']
                                                                          for each in j_txn["vout"]])
            if j_txn["confirmations"] > 6 and addr in addresses:
                return True
    elif coin == "eth":
        if txn_res and addr_res:
            return True if txn_res.get("status", None) == "1" and addr_res.get("status", None) == "1" else False
    return False