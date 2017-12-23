from django import forms
from models import Packages

class packages_form(forms.ModelForm):
    class Meta:
    	model = Packages
    	fields = ['user', 'price', 'description', 'expiry_status','expiry_date']
	# price = forms.CharField(label='Your name', max_length=100)
	# description = forms.CharField(label='Your name', max_length=100)
	# expiry_status = forms.CharField(label='Your name', max_length=100)
	# expiry_date  = forms.CharField(label='Your name', max_length=100)

# class student_create_form(forms.ModelForm):
# 	class Meta:
# 		model = Student
# 		fields = ['student_name','student_enroll','class_name','school']