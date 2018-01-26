from django import forms
from models import Packages

class packages_form(forms.ModelForm):
    class Meta:
    	model = Packages
    	fields = ['price', 'description']
	# price = forms.CharField(label='Your name', max_length=100)
	# description = forms.CharField(label='Your name', max_length=100)
	# expiry_status = forms.CharField(label='Your name', max_length=100)
	# expiry_date  = forms.CharField(label='Your name', max_length=100)
