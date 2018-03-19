# runs one time
import datetime
from pytz import UTC
from avicrypto.settings import EPOCH_BEGIN
from addons.accounts.models import User
from addons.packages.models import User_packages
from addons.transactions.models import Transactions
from addons.wallet.models import Wallet
from addons.packages.lib.payout import  get_package, run_scheduler, calculate_investment, run_investment_calc, find_next_monday

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q

def reset_these():
    # users = User.objects.all()
    # delete all avicrypto wallet and Transactions
    avicrypto_user = User.objects.get(username='harshul', email = 'harshul.kaushik@avicrypto.us')
    avicrypto_wallet = Wallet.objects.filter(owner=avicrypto_user, wallet_type='AW')
    avicrypto_btc = Wallet.objects.filter(owner=avicrypto_user, wallet_type='BTC')
    avicrypto_eth = Wallet.objects.filter(owner=avicrypto_user, wallet_type='ETH')
    avicrypto_xrp = Wallet.objects.filter(owner=avicrypto_user, wallet_type='XRP')
    Transactions.objects.all().exclude(tx_type='W').delete()
    print "All txns except Withdrawal deleted"
    for user in User.objects.all():
        u = user
        # delete all user wallets and Transactions
        user_ROI_wallet = Wallet.objects.filter(owner=user, wallet_type='ROI')
        user_DR_wallet = Wallet.objects.filter(owner=user, wallet_type='DR')
        user_BN_wallet = Wallet.objects.filter(owner=user, wallet_type='BN')
        
    #     # delete all roi/direct/binary received from avicrypto_wallet 
    #     # Transactions.objects.filter(Q(reciever_wallet__in=user_ROI_wallet) | Q(reciever_wallet__in=user_BN_wallet) | Q(reciever_wallet__in=user_DR_wallet)).delete()

        user_ROI_wallet.delete()
        user_DR_wallet.delete()
        user_BN_wallet.delete()

        user_btc = Wallet.objects.filter(owner=user, wallet_type='BTC')
        user_eth = Wallet.objects.filter(owner=user, wallet_type='ETH')
        user_xrp = Wallet.objects.filter(owner=user, wallet_type='XRP')

    #     # delete all transactions to/from user crypto wallets that are not of Withdraw type
    #     # Transactions.objects.filter(Q(sender_wallet__in=user_btc) | 
    #     # Q(reciever_wallet__in=user_btc) | Q(sender_wallet__in=user_eth) | 
    #     # Q(reciever_wallet__in=user_eth) | 
    #     # Q(sender_wallet__in=user_xrp) | 
    #     # Q(reciever_wallet__in=user_xrp)).exclude(tx_type='W').delete()
    #     # Transactions.objects.all().exclude(tx_type='W').delete()

        # user_btc.delete()
        # user_eth.delete()
        # user_xrp.delete()


class Command(BaseCommand):
    help = 'runs and resets few accounts to initial values'

    def handle(self, *args, **options):
        reset_these()
        self.stdout.write(self.style.SUCCESS('Successfully reset'))