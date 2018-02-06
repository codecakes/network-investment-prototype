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
from models import Wallet
from forms import wallet_form

# Create your views here.
class WalletCreate(CreateView):
    template = loader.get_template('wallet.html')
    form_class = wallet_form
    model = Wallet

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(WalletCreate, self).form_valid(form)
    
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
                post.owner = request.user
                post.save()
                return HttpResponse("OK")
        except Exception, e:
            print e
        return HttpResponse("Error")

class WalletList(ListView):
    template = loader.get_template('wallet_list.html')
    model = Wallet

    def get_context_data(self, **kwargs):
        context = super(WalletList, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get(self, request):
        print "get list of wallet", self.template
        wallets = Wallet.objects.filter(owner=request.user)
        print wallets
        context = {
            'wallets': wallets
        }
        return HttpResponse(self.template.render(context, request))