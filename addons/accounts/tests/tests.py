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
from addons.accounts.lib.blockexplorer import validate, is_valid_xrp_paid, is_valid_btc_paid, get_btc, get_xrp

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

class TreeTest(TestCase):
    def setUp(self):
        self.even = [1,2,3,4]
        self.odd = [1,2,3]
    
    def test_divide_conquer_even(self):
        res = divide_conquer(self.even, 0, len(self.even)-1, lambda r: r)
        self.assertEqual(res, self.even, "should be {} but is {}".format(self.even, res))
    
    def test_divide_conquer_odd(self):
        res = divide_conquer(self.odd, 0, len(self.odd)-1, lambda r: r)
        self.assertEqual(res, self.odd, "should be {} but is {}".format(self.odd, res))

class CryptoTransactionTest(TestCase):
    def setUp(self):
        import requests

        self.false_btc = "15VtVKWj1YyHXFAW2uhAfQg1DKdpsjYLgh"
        self.true_btc = "14Eqqo4Sjd46r61rLeHELee7qdbD6tsZBu"
        self.btc_amt = 189420000.0
        self.dest_btc_addr = "1LanezdSwNrG87XquU4V5Bs8QcxTP7gE4f"
        self.btc_txn_id = "006313a1da9f1a82648d0f0f7d2fdb25c42e6fbebf597a03097ec55ecc9089e1"

        self.eth = "0xe5b8b0ee07f1e1ea73052d7af4ec19292c060afe"
        self.eth_txn_id = "0x4dce9e59b8425a0dfc6a9e70b05a6506cc5de2be400509935a8b1076505494cd"
        self.dest_eth_addr = "0xa1cb7c6056ca3924b452f9ed016776dd7c4bce5a"
        self.eth_amt = 604600000000000000.0


        # self.xrp = "rLaKuE49Sg1MjSH6K9nqo3UkCdGkTCLdjQ"
        self.xrp = "rJb5KsHsDHF1YS5B5DU6QCkH5NsPaKQTcy"
        self.xrp_txn_id = "3E04BDFC3C780BDC9792061ECC4B2B60F4DABB0EED123BC5FA74AB8BC15A4DEC"
        self.xrp_amt = 999750000
        self.xrp_dest = "rLdinLq5CJood9wdjY9ZCdgycK8KGevkUj"
        txn_res, _ = get_xrp(self.xrp, self.xrp_txn_id)
        self.xrp_txn_json = txn_res.json()

        

    ########## BTC TXN TESTS ##########

    def test_get_btc_txn_amount(self):
        txn, _ = get_btc(self.true_btc, self.btc_txn_id)
        self.assertEqual(txn["total"], self.btc_amt, "should have equivalent amount. Amt is %s" %(txn["total"]))

    # def test_invalid_btc_txn(self):
    #     self.assertFalse(validate(self.btc_amt, self.dest_btc_addr, self.false_btc, self.btc_txn_id, coin="btc"), "Should have been false BTC Source Address")
    
    
    def test_valid_txref(self):
        _, addr = get_btc(self.true_btc, self.btc_txn_id)
        txrefs = addr.get("txrefs", None)
        self.assertIsNotNone(txrefs, "txrefs key should have value")
        
    def test_valid_txn_hash(self):
        _, addr = get_btc(self.true_btc, self.btc_txn_id)
        txrefs = addr.get("txrefs", None)
        tx_hashes = divide_conquer(txrefs, 0, len(txrefs) - 1, lambda txref: txref["tx_hash"])
        res = any(divide_conquer(tx_hashes, 0, len(tx_hashes) - 1, lambda tx_hash: tx_hash == self.btc_txn_id))
        self.assertTrue(res, "Should contain a valid transaction id")
        
    def test_valid_input_btc_addr(self):
        txn, _ = get_btc(self.true_btc, self.btc_txn_id)
        inputs = txn["inputs"]
        res = self.true_btc in reduce(lambda a, b: a+b, divide_conquer(inputs, 0, len(inputs) - 1, lambda input: input['addresses']))
        self.assertTrue(res, "Should contain a valid btc address. address is %s" %self.true_btc)

    def test_valid_dest_btc_addr(self):
        txn, _ = get_btc(self.true_btc, self.btc_txn_id)
        outputs = txn["outputs"]
        res = self.dest_btc_addr in reduce(lambda a, b: a+b, divide_conquer(outputs, 0, len(outputs) - 1, lambda output: output['addresses']))
        self.assertTrue(res, "Should contain a valid destination btc address. destination address is %s" %self.dest_btc_addr)
    

    def test_is_valid_btc_paid(self):
        txn, addr = get_btc(self.true_btc, self.btc_txn_id)
        res = is_valid_btc_paid(self.btc_amt, self.dest_btc_addr, self.true_btc, self.btc_txn_id, addr, txn)
        res2 = validate(self.btc_amt, self.true_btc, self.dest_btc_addr, self.btc_txn_id)
        self.assertEqual(res, res2, "is_valid_btc_paid and validate should be %s" %res)
    
    ########## XRP TXN TESTS ##########
    def test_xrp_amt(self):
        self.assertEqual(float(self.xrp_txn_json['transaction']['tx']['Amount']), self.xrp_amt, "should be same but type is %s and self.xrp_amt is %s" %(type(self.xrp_txn_json['transaction']['tx']['Amount']), type(self.xrp_amt)))
    
    def test_xrp_dest(self):
        self.assertEqual(self.xrp_txn_json['transaction']['tx']['Destination'], self.xrp_dest, "should be same")
    
    def test_xrp_src(self):
        self.assertEqual(self.xrp_txn_json['transaction']['tx']['Account'], self.xrp, "should be same")

    def test_xrp_txn(self):
        self.assertEqual(self.xrp_txn_json['transaction']['hash'], self.xrp_txn_id, "should be same")
        
    def test_is_valid_xrp_paid(self):
        res = is_valid_xrp_paid(self.xrp_amt, self.xrp_txn_id, self.xrp, self.xrp_dest, self.xrp_txn_json)
        self.assertTrue(res, "xrp txn validation should be True")
    
    def test_validate_xrp(self):
        res = validate(self.xrp_amt, self.xrp, self.xrp_dest, self.xrp_txn_id, coin="xrp")
        res2 = is_valid_xrp_paid(self.xrp_amt, self.xrp_txn_id, self.xrp, self.xrp_dest, self.xrp_txn_json)
        self.assertEqual(res, res2, "xrp transaction should be %s" %res2)
    
    ########## ETH TXN ###########

    def test_eth_txn(self):
        res = validate(self.eth_amt, self.eth, self.dest_eth_addr, self.eth_txn_id, coin="eth")
        self.assertTrue(res, "should be True")


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

class CreateUserTest(TestCase):
    def setUp(self):
        self.package = Packages.objects.create(package_name="USD 1000", package_code="usd1000", payout="7", directout=3.5, binary_payout=6, capping=1000, no_payout=35, loyality=5, roi=2450, price=1000)

        self.user1 = User.objects.create_user(username='user1', password='12345', date_joined=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        User_packages.objects.create(user=self.user1, package=self.package, status="A", created_at=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 3, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user2 = User.objects.create_user(username='self.user2', password='12345', date_joined=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user2.profile.sponser_id = self.user1
        self.user2.profile.placement_id = self.user1
        self.user2.profile.placement_position = 'L'
        self.user2.profile.save()
        Members.objects.create(parent_id=self.user1, child_id=self.user2)
        User_packages.objects.create(user=self.user2, package=self.package, status="A", created_at=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 3, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user3 = User.objects.create_user(username='self.user3', password='12345', date_joined=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user3.profile.sponser_id = self.user1
        self.user3.profile.placement_id = self.user1
        self.user3.profile.placement_position = 'R'
        self.user3.profile.save()
        Members.objects.create(parent_id=self.user1, child_id=self.user3)
        User_packages.objects.create(user=self.user3, package=self.package, status="A", created_at=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 3, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user4 = User.objects.create_user(username='self.user4', password='12345', date_joined=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user4.profile.sponser_id = self.user1
        self.user4.profile.placement_id = self.user2
        self.user4.profile.placement_position = 'L'
        self.user4.profile.save()
        Members.objects.create(parent_id=self.user2, child_id=self.user4)
        User_packages.objects.create(user=self.user4, package=self.package, status="A", created_at=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 3, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user5 = User.objects.create_user(username='self.user5', password='12345', date_joined=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user5.profile.sponser_id = self.user1
        self.user5.profile.placement_id = self.user2
        self.user5.profile.placement_position = 'R'
        self.user5.profile.save()
        Members.objects.create(parent_id=self.user2, child_id=self.user5)
        User_packages.objects.create(user=self.user5, package=self.package, status="A", created_at=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 3, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user6 = User.objects.create_user(username='self.user6', password='12345', date_joined=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user6.profile.sponser_id = self.user1
        self.user6.profile.placement_id = self.user3
        self.user6.profile.placement_position = 'L'
        self.user6.profile.save()
        Members.objects.create(parent_id=self.user3, child_id=self.user6)
        User_packages.objects.create(user=self.user6, package=self.package, status="A", created_at=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 3, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user7 = User.objects.create_user(username='self.user7', password='12345', date_joined=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user7.profile.sponser_id = self.user1
        self.user7.profile.placement_id = self.user3
        self.user7.profile.placement_position = 'R'
        self.user7.profile.save()
        Members.objects.create(parent_id=self.user3, child_id=self.user7)
        User_packages.objects.create(user=self.user7, package=self.package, status="A", created_at=datetime(2018, 3, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 3, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

    def test_case(self):
        self.assertTrue(isinstance(self.user1, User))
        self.assertTrue(is_member_of(self.user1, self.user7), True)