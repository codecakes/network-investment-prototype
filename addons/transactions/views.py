from django.shortcuts import render
from django.views.generic import *
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.template import loader
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db.models.query_utils import Q
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.views.generic import *
from django.contrib import messages
from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
# from django.views.generic.list import ListView
from django.contrib.auth.models import User
# from server.accounts.models import Profile

from addons.packages.models import Packages, User_packages
from addons.wallet.models import Wallet
from models import Transactions
from forms import transactions_form

# Create your views here.
class TransactionsCreate(CreateView):
    template = loader.get_template('transactions.html')
    form_class = transactions_form
    model = Transactions

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(TransactionsCreate, self).form_valid(form)
    
    def get(self, request):
        context ={
            'form':self.form_class
        }
        return HttpResponse(self.template.render(context, request))
    def post(self, request):
        form = self.form_class(request.POST)
        try:
            if form.is_valid():
                data = form.cleaned_data
                post = form.save(commit=False)
                post.user = request.user
                post.save()
                return HttpResponse("OK")
        except Exception, e:
            print e
        return HttpResponse("Error")

class TransactionsList(ListView):
    template = loader.get_template('transactions_list.html')
    model = Transactions

    def get_context_data(self, **kwargs):
        context = super(TransactionsList, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get(self, request):
        transactions = Transactions.objects.filter(sender_wallet=request.user)
        context = {
            'transactions': transactions
        }
        return HttpResponse(self.template.render(context, request))

class TransactionsSummary(ListView):
    template = loader.get_template('transactions.html')
    model = Transactions

    def get_context_data(self, **kwargs):
        context = super(TransactionsSummary, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get(self, request):
        user = request.user
        transactions = Transactions.objects.filter(reciever_wallet__owner=user)
        packages = User_packages.objects.filter(user=user)
        wallets = Wallet.objects.filter(owner=user)
        #  get the current payout of weeks 
        roi = {'till_now':0.0, 'pending':0.0, 'withdraw':0.0, 'total':0.0}
        binary = {'till_now':0.0, 'pending':0.0, 'withdraw':0.0, 'total':0.0}
        direct = {'till_now':0.0, 'pending':0.0, 'withdraw':0.0, 'total':0.0}

        for pkg in packages:
            roi['till_now'] += pkg.weekly
            binary['till_now'] += pkg.binary
            direct['till_now'] += pkg.direct
# get the total paid withdraw 
        for txns in transactions:
            if txns.status == 'paid' and txns.tx_type == 'roi':
                roi['withdraw'] += txns.amount
            elif txns.status == 'P' or txns.status=='C' or txns.status=='processing' and txns.tx_type == 'roi':
                roi['pending'] += txns.amount
            elif txns.status == 'paid' and txns.tx_type == 'binary':
                binary['withdraw'] += txns.amount
            elif txns.status == 'P' or txns.status=='C' or txns.status=='processing' and txns.tx_type == 'roi':
                binary['pending'] += txns.amount
            elif txns.status == 'paid' and txns.tx_type == 'direct':
                direct['withdraw'] += txns.amount
            elif txns.status == 'P' or txns.status=='C' or txns.status=='processing' and txns.tx_type == 'roi':
                direct['pending'] += txns.amount

        roi['total'] = float(sum(roi.values()))
        binary['total'] = float(sum(binary.values()))
        direct['total'] = float(sum(direct.values()))
        
        context = {
            'roi':roi,
            'binary':binary,
            'direct':direct,
            'packages': packages,
            'transactions': transactions,
            'wallets': wallets,
            'transaction_status_choices': Transactions.status_choices,
            'userpackage_status_choices': User_packages.status_choices,
        }
        return HttpResponse(self.template.render(context, request))