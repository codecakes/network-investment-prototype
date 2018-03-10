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
from addons.packages.lib.payout import get_package, calc, calc_weekly, calc_leg, START_TIME, get_direct_pair, get_user_from_member, get_active_mem_price, filter_by_sponsor, find_next_monday, valid_payout_user, filter_by_leg_user, run_investment_calc
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

class TreeFunctionTest(TestCase):
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
        self.UTC = pytz.UTC
        tz = lambda r: (self.UTC.localize(r))
        
        self.packageA = Packages.objects.create(package_name="USD 5000", package_code="usd5000", payout="7.5", directout=3.5, binary_payout=6, capping=5000, no_payout=35, loyality=5, roi=2450, price=5000)
        self.userA = User.objects.create_user(username='userA', password='12345', date_joined=tz(datetime(2018, 01, 03, 00, 8, 7)))
        self.UserpackagesA = User_packages.objects.create(user=self.userA, package=self.packageA, status="A", created_at=(datetime(2018, 02, 03, 00, 8, 7, 127325, tzinfo=pytz.UTC)), last_payout_date=(datetime(2018, 02, 03, 00, 8, 7, 127325, tzinfo=pytz.UTC)), duration=1)
        self.UserpackagesA.created_at = datetime(2018, 02, 03, 00, 8, 7, 127325, tzinfo=pytz.UTC)
        self.UserpackagesA.save(update_fields=['created_at'])
        

        self.package = Packages.objects.create(package_name="USD 1000", package_code="usd1000", payout="7", directout=3.5, binary_payout=6, capping=1000, no_payout=35, loyality=5, roi=2450, price=1000)

        self.user1 = User.objects.create_user(username='user1', password='12345', date_joined=tz(datetime(2018, 2, 11, 20, 8, 7, 127325)))
        self.pkg1 = User_packages.objects.create(user=self.user1, package=self.package, status="A", created_at=(datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC)), last_payout_date=(datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC)), duration=1)
        self.pkg1.created_at = datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC)
        self.pkg1.save(update_fields=['created_at'])

        self.user2 = User.objects.create_user(username='self.user2', password='12345', date_joined=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user2.profile.sponser_id = self.user1
        self.user2.profile.placement_id = self.user1
        self.user2.profile.placement_position = 'L'
        self.user2.profile.save()

        Members.objects.create(parent_id=self.user1, child_id=self.user2)
        User_packages.objects.create(user=self.user2, package=self.package, status="A", created_at=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 2, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user3 = User.objects.create_user(username='self.user3', password='12345', date_joined=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user3.profile.sponser_id = self.user1
        self.user3.profile.placement_id = self.user1
        self.user3.profile.placement_position = 'R'
        self.user3.profile.save()
        Members.objects.create(parent_id=self.user1, child_id=self.user3)
        User_packages.objects.create(user=self.user3, package=self.package, status="A", created_at=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 2, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user4 = User.objects.create_user(username='self.user4', password='12345', date_joined=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user4.profile.sponser_id = self.user1
        self.user4.profile.placement_id = self.user2
        self.user4.profile.placement_position = 'L'
        self.user4.profile.save()
        Members.objects.create(parent_id=self.user2, child_id=self.user4)
        User_packages.objects.create(user=self.user4, package=self.package, status="A", created_at=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 2, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user5 = User.objects.create_user(username='self.user5', password='12345', date_joined=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user5.profile.sponser_id = self.user1
        self.user5.profile.placement_id = self.user2
        self.user5.profile.placement_position = 'R'
        self.user5.profile.save()
        Members.objects.create(parent_id=self.user2, child_id=self.user5)
        User_packages.objects.create(user=self.user5, package=self.package, status="A", created_at=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 2, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user6 = User.objects.create_user(username='self.user6', password='12345', date_joined=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user6.profile.sponser_id = self.user1
        self.user6.profile.placement_id = self.user3
        self.user6.profile.placement_position = 'L'
        self.user6.profile.save()
        Members.objects.create(parent_id=self.user3, child_id=self.user6)
        User_packages.objects.create(user=self.user6, package=self.package, status="A", created_at=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 2, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.user7 = User.objects.create_user(username='self.user7', password='12345', date_joined=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC))
        self.user7.profile.sponser_id = self.user1
        self.user7.profile.placement_id = self.user3
        self.user7.profile.placement_position = 'R'
        self.user7.profile.save()
        Members.objects.create(parent_id=self.user3, child_id=self.user7)
        User_packages.objects.create(user=self.user7, package=self.package, status="A", created_at=datetime(2018, 2, 11, 20, 8, 7, 127325, tzinfo=pytz.UTC), last_payout_date=datetime(2018, 2, 12, 20, 8, 7, 127325, tzinfo=pytz.UTC), duration=1)

        self.next_date = self.UTC.normalize(self.UTC.localize(datetime(2018, 02, 19, 00, 00, 00, 00)))

        self.avicrypto_user = User.objects.create(username='harshul', email = 'harshul.kaushik@avicrypto.us')
        self.avicrypto_user.set_password('avi1234')
        self.avicrypto_user.save()

    def test_avicrypto_user(self):
        self.assertTrue(self.avicrypto_user)

    def test_case(self):
        self.assertTrue(isinstance(self.user1, User))
        self.assertTrue(is_member_of(self.user1, self.user7), True)
    
    
    ########### CALCULATE WEEKLY #############
    def test_date_cmp(self):
        next_date = self.UTC.normalize(self.UTC.localize(datetime(2018, 02, 26)))
        self.assertLess(self.userA.date_joined, next_date, "User DOJ should be less than next_date")
    
    def test_date(self):
        pkg = get_package(self.userA)
        pkg_tm = self.UTC.normalize(pkg.created_at)
        dt = datetime(2018, 02, 03, 00, 8, 7, 127325, tzinfo=pytz.UTC)
        self.assertEqual(pkg_tm.isoformat(), dt.isoformat(), "Should be equal but is {} and {}".format(pkg_tm, dt))
    
    def test_pkg_less(self):
        pkg = get_package(self.userA)
        pkg_tm = self.UTC.normalize(pkg.created_at)
        next_date = self.UTC.normalize(self.UTC.localize(datetime(2018, 02, 26)))
        self.assertLess(pkg_tm.date(), next_date.date(), "Pkg creation should be < next_date but are {} and {}".format(pkg_tm.date(), next_date.date()))

    def test_weekly(self):
        next_date = self.UTC.normalize(self.UTC.localize(datetime(2018, 02, 26, 00, 00, 00, 00)))
        res, _ = calc_weekly(self.userA, self.userA.date_joined, next_date)
        self.assertEqual(res, 1125, "should be 1125 but is %s" %res)

    def test_calc_weekly(self):
        print "self.pkg1.created_at is ", self.pkg1.created_at
        res, _ = calc(self.user1, self.pkg1.created_at, 'weekly')
        self.assertEqual(res, 280, "should've been 280 but is %s" %res)
    
    
    def test_all_members_traversed(self):
        tot = [self.user1]
        members = Members.objects.filter(parent_id=self.user1)
        [tot.append(m) for m in members]
        while members:    
            members = reduce(lambda x, y: x|y, divide_conquer(members, 0, len(members)-1, get_user_from_member))
            [tot.append(m) for m in members]
        # print "users are: {}".format([m.child_id.username if type(m)==Members else m.username for m in tot])
        self.assertEqual(len(tot), 7, "should be 7 users in all but are: %s" %(len(tot)))
    
    def test_tot_package_sum(self):
        "find total package sum of all users"
        res = sum(map(lambda u: get_active_mem_price(u), User.objects.all()))
        self.assertEqual(res, 12000, "total package sum should be 12000 but is %s" %res)
    
    def test_valid_payout_user(self):
        "validate if a user has last_date <= doj < next_date is s.t."
        sponsor_id = self.user1.profile.user_auto_id
        last_date = self.user1.date_joined
        next_date =  self.next_date
        members = Members.objects.filter(parent_id=self.user1)
        bl = valid_payout_user(sponsor_id, members[0], last_date, next_date)
        self.assertTrue(bl, "should be True but is %s" %bl)
        
    
    def test_filter_valid_users(self):
        "find valid users for calculation between last_date and next_date"
        filtered_members = []
        sponsor_id = self.user1.profile.user_auto_id
        last_date = self.user1.date_joined
        next_date =  self.next_date
        members = Members.objects.filter(parent_id=self.user1)
        while members:
            filtered_members.extend(filter_by_sponsor(sponsor_id, last_date, next_date, members))
            members = reduce(lambda x, y: x|y, divide_conquer(members, 0, len(members)-1, get_user_from_member))
        
        self.assertEqual(len(filtered_members), 6, "should be 6 but is {}".format(len(filtered_members)))

    def test_calc_left_leg(self):
        """Calculate left leg sum"""
        last_date = self.user1.date_joined
        next_date =  self.next_date
        res = calc_leg(self.user1, last_date, next_date, leg='l')
        self.assertEqual(res, 3000, "left leg sum should be 3000 but is %s" %res)
    
    def test_calc_right_leg(self):
        """Calculate right leg sum"""
        last_date = self.user1.date_joined
        next_date =  self.next_date
        res = calc_leg(self.user1, last_date, next_date, leg='r')
        self.assertEqual(res, 3000, "right leg sum should be 3000 but is %s" %res)

    
    ####### CALCULATE DIRECT ########
    def test_calc_direct(self):
        res, _ = calc(self.user1, self.user1.date_joined, 'direct')
        self.assertEqual(res, 210, "should've been 210 but is {}".format(res))
    

    ########## CALCULATE BINARY ##########
    def test_filter_by_sponsor(self):
        sponsor_id = self.user1.profile.user_auto_id
        members = Members.objects.filter(parent_id=self.user1.id)
        fl_mem = filter_by_sponsor(sponsor_id, self.user1.date_joined, self.next_date, members)
        self.assertTrue(fl_mem, "Should have members but is {}".format(fl_mem))
    
    def test_filter_by_left_leg_user(self):
        sponsor_id = self.user1.profile.user_auto_id
        members = Members.objects.filter(parent_id=self.user1.id)
        fl_mem = filter_by_sponsor(sponsor_id, self.user1.date_joined, self.next_date, members)
        left_mem = filter(lambda m: LEG['l'](m), fl_mem)
        self.assertEqual(len(left_mem), 1, "should be 1 but is %s" %(len(left_mem)))
    
    def test_get_direct_pair(self):
        res = get_direct_pair(self.user1, self.user1.date_joined, self.next_date)
        self.assertTrue(res, "Is %s" %res)

    def test_calc_binary(self):
        res, _ = calc(self.user1, self.user1.date_joined, 'binary')
        # print res
        self.assertEqual(res[0], 180, "Should be 180 but is %s" %res[0])

    def test_run_investment_calc(self):
        pkg = get_package(self.user1)
        next_date = self.UTC.normalize(self.UTC.localize(datetime(2018, 03, 05)))
        print "pkg.created_at {} pkg.last_payout_date {}".format(pkg.created_at, pkg.last_payout_date)
        run_investment_calc(self.user1, pkg, pkg.created_at, next_date, admin=self.avicrypto_user)
        pkg = get_package(self.user1)
        print [pkg.binary, pkg.direct, pkg.weekly]
        self.assertListEqual([pkg.binary, pkg.direct, pkg.weekly], [180, 210, 140], "Failed. value is {}".format([pkg.binary, pkg.direct, pkg.weekly]))