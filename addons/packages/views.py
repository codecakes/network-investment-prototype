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
from django.utils import timezone
# from django.views.generic.list import ListView
from django.contrib.auth.models import User
# from server.accounts.models import Profile
from models import Packages, User_packages
from forms import packages_form
from datetime import date

def add_years(d, years):
    try:
        return d.replace(year = d.year + years)
    except ValueError:
        return d + (date(d.year + years, 3, 1) - date(d.year, 3, 1))

# Create your views here.
def PackagesCreate(request):
    context = {
        "packages": Packages.objects.all()
    }

    if request.method == "POST":
        user = request.user
        package_id = request.POST.get("package", "1")
        duration = int(request.POST.get("duration", 1))

        package = Packages.objects.get(id=package_id)
        expiry_date = add_years(timezone.now(), duration) 

        user_package = User_packages(package=package, user=user, duration=duration, status="NA", expiry_date=expiry_date)
        user_package.save()

    template = loader.get_template('packages.html')
    return HttpResponse(template.render(context, request))

class PackagesList(ListView):
    template = loader.get_template('packages_list.html')
    model = Packages

    def get_context_data(self, **kwargs):
        context = super(PackagesList, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get(self, request):
        packages = Packages.objects.all()
        context = {
            'packages':packages
        }
        return HttpResponse(self.template.render(context, request))

class PackagesBList(ListView):
    template = loader.get_template('packages_b_list.html')
    model = Packages

    def get_context_data(self, **kwargs):
        context = super(PackagesList, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

    def get(self, request):
        packages = Packages.objects.all()
        context = {
            'packages': packages
        }
        return HttpResponse(self.template.render(context, request))