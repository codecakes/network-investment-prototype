# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.conf import settings
from django.contrib.auth.models import User
from addons.accounts.models import Profile, Members
from addons.packages.models import Packages, User_packages

import pytz
import calendar
from datetime import datetime, timedelta
from addons.accounts.lib.tree import load_users, find_min_max, is_member_of, is_parent_of, is_valid_leg, has_child, LEG, divide_conquer, get_left, get_right
from addons.packages.lib.payout import calc, START_TIME

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

class LogInTest(TestCase):
    def setUp(self):
        self.credentials = {
            'username': 'testuser',
            'password': 'testpassword'}
        User.objects.create_user(**self.credentials)
    def test_login(self):
        # send login data
        response = self.client.post('/login/', self.credentials, follow=True)
        # should be logged in now
        self.assertTrue(response.context['user'].is_active)
