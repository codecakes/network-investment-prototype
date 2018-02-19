"""avicrypto URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from . import views
# from views import ResetPasswordRequestView

urlpatterns = [
    url(r'^add/$', login_required(views.TransactionsCreate.as_view()), name='transactions_create'),
    url(r'^list/$', views.TransactionsList.as_view(), name='transactions_list'),
    url(r'^summary/$', login_required(views.TransactionsSummary.as_view()), name='transactions_list'),
]
