# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings

from addons.accounts.models import User, Members
from addons.packages.models import Packages, User_packages

# from django.contrib.auth.models import User
from addons.accounts.models import Profile, Members
from addons.packages.models import Packages, User_packages

import pytz
import calendar
from datetime import datetime, timedelta
from addons.accounts.lib.tree import load_users, find_min_max, is_member_of, is_parent_of, is_valid_leg, has_child, LEG, divide_conquer, get_left, get_right
from addons.packages.lib.payout import calc, START_TIME
from addons.accounts.lib.blockexplorer import validate, is_valid_xrp_paid, is_valid_btc_paid, get_btc

# TODO: Do it in time
# class BinaryTestCase(TestCase):
#     """Tests out binary payment"""
    
#     def setUp(self):
#         self.root_user = User.objects.get(email="cryptocoin.inbox@gmail.com")
#         self.left_user = get_left(self.root_user)
#         self.right_user = get_right(self.root_user)
    
#     def test_left_user_active_pkg(self):
#         root_pkg = User_packages.objects.get(user = self.root_user)
#         self.assertEqual(root_pkg.package.price, 1000, "Package should be $ 1000")
#         # self.left_user

class CryptoTransactionTest(TestCase):
    def setUp(self):
        self.false_btc = "15VtVKWj1YyHXFAW2uhAfQg1DKdpsjYLgh"
        self.true_btc = "14Eqqo4Sjd46r61rLeHELee7qdbD6tsZBu"
        self.btc_amt = 189420000.0
        self.dest_btc_addr = "1LanezdSwNrG87XquU4V5Bs8QcxTP7gE4f"
        self.btc_txn_id = "006313a1da9f1a82648d0f0f7d2fdb25c42e6fbebf597a03097ec55ecc9089e1"

        self.eth = "0xe5b8b0ee07f1e1ea73052d7af4ec19292c060afe"
        self.xrp = "rLaKuE49Sg1MjSH6K9nqo3UkCdGkTCLdjQ"
        self.xrp_txn_id = "3E04BDFC3C780BDC9792061ECC4B2B60F4DABB0EED123BC5FA74AB8BC15A4DEC"
        

    def test_get_btc_txn_amount(self):
        addr, txn = get_btc(self.true_btc, self.btc_txn_id)
        self.assertEqual(txn["total"], self.btc_amt, "should have equivalent amount. Amt is %s" %(txn["total"]))

    def test_invalid_btc_txn(self):
        self.assertFalse(validate(self.btc_amt, self.dest_btc_addr, self.false_btc, self.btc_txn_id, coin="btc"), "Should have been false BTC Source Address")
    
    
    def test_valid_txref(self):
        addr, txn = get_btc(self.true_btc, self.btc_txn_id)
        txrefs = dict.get(addr, "txrefs", None)
        self.assertIsNotNone(txrefs, "txrefs key should have value")
        
    def test_valid_txn_hash(self):
        addr, txn = get_btc(self.true_btc, self.btc_txn_id)
        txrefs = dict.get(addr, "txrefs", None)
        tx_hashes = divide_conquer(txrefs, 0, len(txrefs) - 1, lambda txref: txref["tx_hash"])
        res = any(divide_conquer(tx_hashes, 0, len(tx_hashes) - 1, lambda tx_hash: tx_hash == self.btc_txn_id))
        self.assertTrue(res, "Should contain a valid transaction id")
        
    def test_valid_input_btc_addr(self):
        addr, txn = get_btc(self.true_btc, self.btc_txn_id)
        inputs = txn["inputs"]
        res = self.true_btc in reduce(lambda a, b: a+b, divide_conquer(inputs, 0, len(inputs) - 1, lambda input: input['addresses']))
        self.assertTrue(res, "Should contain a valid btc address. address is %s" %self.true_btc)

    def test_valid_dest_btc_addr(self):
        addr, txn = get_btc(self.true_btc, self.btc_txn_id)
        outputs = txn["outputs"]
        res = self.dest_btc_addr in reduce(lambda a, b: a+b, divide_conquer(outputs, 0, len(outputs) - 1, lambda output: output['addresses']))
        self.assertTrue(res, "Should contain a valid destination btc address. destination address is %s" %self.dest_btc_addr)
    

    def test_is_valid_btc_paid(self):
        addr, txn = get_btc(self.true_btc, self.btc_txn_id)
        res = is_valid_btc_paid(self.btc_amt, self.dest_btc_addr, self.true_btc, self.btc_txn_id, addr, txn)
        res2 = validate(self.btc_amt, self.dest_btc_addr, self.true_btc, self.btc_txn_id)
        
        print "test_is_valid_btc_paid : %s" %res
        print "BUt VALIDATE IS : %s" %res2
        self.assertEqual(res, res2, "is_valid_btc_paid and validate should be TRUE")
        
    def test_valid_btc_txn(self):
        res = validate(self.btc_amt, self.dest_btc_addr, self.true_btc, self.btc_txn_id, coin="btc")
        self.assertTrue(res, "Should validate BTC Source Address but returns: %s" %res)


# class LogInTest(TestCase):
#     def setUp(self):
#         self.credentials = {
#             'username': 'testuser',
#             'password': 'testpassword'}
#         User.objects.create_user(**self.credentials)
#     def test_login(self):
#         # send login data
#         response = self.client.post('/login/', self.credentials, follow=True)
#         # should be logged in now
#         self.assertTrue(response.context['user'].is_authenticated)
