from django import forms
from models import Wallet

class wallet_form(forms.ModelForm):
    
    class Meta:
    	model = Wallet
    	fields = ['wallet_type', 'amount', 'description']	