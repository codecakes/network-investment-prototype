from urllib2 import urlparse
import requests
from addons.accounts.lib.tree import divide_conquer
import django_rq
import blockcypher
import logging

logging.basicConfig(level=logging.WARNING)

QUEUE = django_rq.get_queue('crypto_payments', autocommit=True, async=True)


BTC_HOST = "https://blockexplorer.com/"
ETH_HOST = "https://api.etherscan.io"
XRP_HOST = "https://data.ripple.com"

BTC_API = "e186532e40724e268c20ac8cf0e19973"
ETHER_KEY = "6F98VB1ZJ6MY46JHZ9AVR6YJQJPU3RCH95"

def get_endpoints(api_host, txn_endpoint, coin_endpoint):
    txn_api = urlparse.urljoin(api_host, txn_endpoint)
    addr_api = urlparse.urljoin(api_host, coin_endpoint)
    return [txn_api, addr_api]


def get_btc(addr, txn_id):
    # txn_endpoint = "api/tx/%s" % (txn_id)
    # coin_endpoint = "api/addr/%s" % (addr)
    # return get_endpoints(BTC_HOST, txn_endpoint, coin_endpoint)
    return [blockcypher.get_transaction_details(txn_id, api_key=BTC_API), blockcypher.get_address_details(addr, api_key=BTC_API)]


def get_eth(addr, txn_id):
    txn_endpoint = "api?module=transaction&action=gettxreceiptstatus&txhash=%s&apikey=%s" % (
        txn_id, ETHER_KEY)
    coin_endpoint = "api?module=account&action=balance&address=%s&tag=latest&apikey=%s" % (
        addr, ETHER_KEY)
    txn_api, addr_api = get_endpoints(ETH_HOST, txn_endpoint, coin_endpoint)
    return [requests.get(txn_api), requests.get(addr_api)]


def get_xrp(addr, txn_id):
    txn_endpoint = "v2/transactions/%s" % (txn_id)
    coin_endpoint = "v2/accounts/%s/transactions" % (addr)
    txn_api, addr_api = get_endpoints(XRP_HOST, txn_endpoint, coin_endpoint)
    return [requests.get(txn_api), requests.get(addr_api)]


COIN = {
    "btc": get_btc,
    "eth": get_eth,
    "xrp": get_xrp
}


def is_valid_btc_paid(amt, dest_addr, addr, txn_id, j_addr, j_txn):
    txrefs = j_addr.get("txrefs", None)
    if txrefs is not None:    
        tx_hashes = divide_conquer(txrefs, 0, len(txrefs) - 1, lambda txref: txref["tx_hash"])
        inputs = j_txn["inputs"]
        outputs = j_txn["outputs"]
        total_amt = j_txn["total"]
        return (total_amt == amt) and any(divide_conquer(tx_hashes, 0, len(tx_hashes) - 1, lambda tx_hash: tx_hash == txn_id)) and (addr in reduce(lambda a, b: a+b, divide_conquer(inputs, 0, len(inputs) - 1, lambda input: input['addresses']))) and (dest_addr in reduce(lambda a, b: a+b, divide_conquer(outputs, 0, len(outputs) - 1, lambda output: output['addresses'])))
    return False
    
def is_valid_xrp_paid(amt, txn_id, addr, dest_addr, txn):
    txn_json = txn['transaction']['tx']
    return float(txn_json['Amount']) == amt and txn_json['Destination'] == dest_addr and txn_json['Account'] == addr and txn['transaction']['hash'] == txn_id

def valid_ether(r, amt, src_addr, dest_addr, txn_id):
    return (amt == float(r["value"]) and src_addr == r['from'] and dest_addr == r['to'] and txn_id == r['hash'])


def is_valid_eth_paid(amt, src_addr, addr, txn_id, txn_res):
    # print txn_res
    result = txn_res['result']
    return any(divide_conquer(result, 0, len(result) - 1, lambda r: valid_ether(r, amt, src_addr, addr, txn_id)))
    # return any([valid_ether(r, amt, src_addr, addr, txn_id) for r in result])


def validate(amt, src_addr, addr, txn_id, coin="btc"):
    """Validates the given address and transaction of the given crypto payment type which can by anyone of BTC, ETH, XRP"""
    txn_res, addr_res = COIN[coin](src_addr, txn_id)
    assert coin in ("btc", "eth", "xrp")
    if coin == "btc":
        return is_valid_btc_paid(amt, addr, src_addr, txn_id, addr_res, txn_res)
    elif coin == "eth":
        txn_res = txn_res.json()
        addr_res = addr_res.json()
        if (txn_res.get("status", None) == "1" and addr_res.get("status", None) == "1"):
            uri = "api?module=account&action=txlist&address=%s&startblock=0&endblock=99999999&sort=asc&apikey=%s" %(src_addr, ETHER_KEY)
            res = requests.get(urlparse.urljoin(ETH_HOST, uri)).json()
            return is_valid_eth_paid(amt, src_addr, addr, txn_id, res)
    elif coin == "xrp":
        j_txn = txn_res.json()
        j_addr = addr_res.json()
        if j_addr['result'] == "success" and j_txn['result'] == "success":
            return is_valid_xrp_paid(amt, txn_id, src_addr, addr, j_txn)
    raise Exception("you should not be here")
    

def validate_transaction(amt, src_addr, addr, txn_id, coin="btc"):
    """
    Async RQ job worker into apscheduler
    """
    # QUEUE.enqueue(validate, amt, src_addr, addr, txn_id, coin=coin)
    job = QUEUE.enqueue_call(func=validate,
               args=(amt, src_addr, addr, txn_id),
               kwargs={coin: coin},
               job_id=addr)
    job.meta['addr'] = addr
    job.meta['amt'] = amt
    return