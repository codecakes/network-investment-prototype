from urllib2 import urlparse
import requests
from addons.accounts.lib.tree import divide_conquer

ETHER_KEY = "6F98VB1ZJ6MY46JHZ9AVR6YJQJPU3RCH95"

BTC_HOST = "https://blockexplorer.com/"
ETH_HOST = "https://api.etherscan.io"
XRP_HOST = "https://data.ripple.com"


def get_endpoints(api_host, txn_endpoint, coin_endpoint):
    txn_api = urlparse.urljoin(api_host, txn_endpoint)
    addr_api = urlparse.urljoin(api_host, coin_endpoint)
    return [txn_api, addr_api]


def get_btc(addr, txn_id):
    txn_endpoint = "api/tx/%s" % (txn_id)
    coin_endpoint = "api/addr/%s" % (addr)
    return get_endpoints(BTC_HOST, txn_endpoint, coin_endpoint)


def get_eth(addr, txn_id):
    txn_endpoint = "api?module=transaction&action=gettxreceiptstatus&txhash=%s&apikey=%s" % (
        txn_id, ETHER_KEY)
    coin_endpoint = "api?module=account&action=balance&address=%s&tag=latest&apikey=%s" % (
        addr, ETHER_KEY)
    return get_endpoints(ETH_HOST, txn_endpoint, coin_endpoint)


def get_xrp(addr, txn_id):
    txn_endpoint = "v2/transactions/%s" % (txn_id)
    coin_endpoint = "v2/accounts/%s/transactions" % (addr)
    return get_endpoints(XRP_HOST, txn_endpoint, coin_endpoint)


COIN = {
    "btc": get_btc,
    "eth": get_eth,
    "xrp": get_xrp
}


def is_valid_xrp_paid(amt, txn_id, addr, src_addr, payment):
    return payment.amount == amt and payment.source == src_addr and payment.destination == addr, payment.tx_hash == txn_id


def validate_transaction(amt, src_addr, addr, txn_id, coin="btc"):
    """Validates the given address and transaction of the given crypto payment type which can by anyone of BTC, ETH, XRP"""
    txn_api, addr_api = COIN[coin](addr, txn_id)
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
    elif coin == "xrp":
        j_txn = txn_res.json()
        j_addr = addr_res.json()
        if j_addr.result != "error" and j_txn.result != "error":
            payments = j_txn.payments
            return divide_conquer(payments, 0, len(payments) - 1, lambda payment: is_valid_xrp_paid(amt, txn_id, addr, src_addr, payment))
    return False
