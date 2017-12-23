from django import forms
from models import Transactions

class transactions_form(forms.ModelForm):
    class Meta:
    	model = Transactions
    	fields = ['sender_wallet', 'reciever_wallet', 'description', 'amount']