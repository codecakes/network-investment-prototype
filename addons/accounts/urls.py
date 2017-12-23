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

from . import views
# from views import ResetPasswordRequestView

urlpatterns = [
	url(r'^$', views.index, name='index'),
    url(r'^login$', views.login_fn, name='login'),
    url(r'^signup', views.Registration.as_view(), name='signup'),
    url(r'^home', views.home, name='dashboard'),
    url(r'^thanks$', views.thanks, name='thanks'),
    url(r'^error$', views.error, name='Error'),
    # url(r'logout', views.logout_fn, name='Secure logout'),
]

